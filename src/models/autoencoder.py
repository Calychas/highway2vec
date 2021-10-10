import torch
from torch import nn
from torch import optim
import torch.nn.functional as F
import pytorch_lightning as pl
from torch_geometric.nn import GCNConv
from torch_geometric.nn import GAE


class LitAutoEncoder(pl.LightningModule):
    def __init__(self, in_dim: int, hidden_dim: int = 64, code_dim: int = 3):
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

    def forward(self, x):
        embedding = self.encoder(x)
        return embedding

    def training_step(self, x, batch_idx):
        x = x.view(x.size(0), -1)
        z = self.encoder(x)
        x_hat = self.decoder(z)
        loss = F.mse_loss(x_hat, x)

        self.log('train_loss', loss, on_epoch=True, on_step=True)
        return loss

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=1e-3)
        return optimizer



class GCNEncoder(pl.LightningModule):
    def __init__(self, in_channels, out_channels) -> None:
        super(GCNEncoder, self).__init__()
        self.conv1 = GCNConv(in_channels, 2 * out_channels, cached=True) # cached only for transductive learning
        self.conv2 = GCNConv(2 * out_channels, out_channels, cached=True) # cached only for transductive learning

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        return self.conv2(x, edge_index)


class LitGAE(pl.LightningModule):
    def __init__(self, encoder, decoder=None) -> None:
        super().__init__()
        self.gae = GAE(encoder, decoder)

    def encode(self, x, edge_index):
        return self.gae.encode(x, edge_index)

    def decode(self, z, sigmoid=True):
        return self.gae.decode(z, sigmoid)

    def forward(self, x, edge_index):
        z = self.gae.encode(x, edge_index)
        return z
    
    def training_step(self, batch, batch_idx):
        x, edge_index = batch
        z = self.encode(x, edge_index)
        # x_hat = self.decode(z)
        loss = self.gae.recon_loss(z, edge_index)

        self.log('train_loss', loss, on_epoch=True, on_step=True)
        return loss

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=1e-3)
        return optimizer
    