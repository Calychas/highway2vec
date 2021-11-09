import torch
from torch import nn
from torch import optim
import torch.nn.functional as F
import pytorch_lightning as pl
from torch_geometric.nn import GCNConv
from torch_geometric.nn import GAE


class LitAutoEncoder(pl.LightningModule):
    def __init__(self, in_dim: int, hidden_dim: int = 64, code_dim: int = 3, lr: float = 1e-3):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, code_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(code_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, in_dim),
        )
        self.lr = lr

    def forward(self, x):
        z = self.encoder(x)
        return z

    def training_step(self, batch, batch_idx):
        return self._common_step(batch, batch_idx, 'train')

    def validation_step(self, batch, batch_idx):
        return self._common_step(batch, batch_idx, 'val')

    def test_step(self, batch, batch_idx):
        return self._common_step(batch, batch_idx, 'test')

    def _prepare_batch(self, batch, batch_idx):
        x = batch
        # x = x.view(x.size(0), -1)
        return x

    def _common_step(self, batch, batch_idx, stage: str) -> torch.Tensor:
        x = self._prepare_batch(batch, batch_idx)
        z = self.encoder(x)
        x_hat = self.decoder(z)
        loss = F.mse_loss(x_hat, x)

        self.log(f'{stage}_loss', loss, on_epoch=True, on_step=True, prog_bar=True)

        return loss

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=self.lr)
        return optimizer



class GCNEncoder(pl.LightningModule):
    def __init__(self, in_channels, out_channels) -> None:
        super().__init__()
        self.conv1 = GCNConv(in_channels, 2 * out_channels)
        self.conv2 = GCNConv(2 * out_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        return self.conv2(x, edge_index)


class LitGAE(pl.LightningModule):
    def __init__(self, encoder, decoder=None) -> None:
        super().__init__()
        self.gae = GAE(encoder, decoder)

    def encode(self, x, edge_index):
        return self.gae.encode(x, edge_index)

    def decode(self, z, edge_index, sigmoid=True):
        return self.gae.decode(z, edge_index, sigmoid)

    def forward(self, x, edge_index):
        z = self.gae.encode(x, edge_index)
        return z
    
    def training_step(self, batch, batch_idx):
        x = batch.x
        edge_index = batch.edge_index
        z = self.encode(x, edge_index)
        x_hat = self.decode(z, edge_index)
        loss = self.gae.recon_loss(z, edge_index)

        self.log('train_loss', loss, on_epoch=True, on_step=True)
        return loss

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=1e-3)
        return optimizer
    