import torch
from torch import nn
from torch import optim
import torch.nn.functional as F
import pytorch_lightning as pl
from torch_geometric.nn import GCNConv
from torch_geometric.nn import GAE


class LitAutoEncoder(pl.LightningModule):
    def __init__(self, in_dim: int, hidden_dim: int = 64, latent_dim: int = 3, lr: float = 1e-3):
        super().__init__()

        self.save_hyperparameters()

        self.encoder = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
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


class LitVAE(pl.LightningModule):
    def __init__(self, in_dim: int, hidden_dim: int = 64, enc_out_dim: int = 32, latent_dim: int = 3, lr: float = 1e-3, kl_coeff: float = 0.1):
        super().__init__()

        self.save_hyperparameters()

        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.enc_out_dim = enc_out_dim
        self.latent_dim = latent_dim
        self.kl_coeff = kl_coeff
        self.lr = lr

        self.encoder = nn.Sequential(
            nn.Linear(self.in_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.enc_out_dim),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(self.latent_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.in_dim),
        )

        self.fc_mu = nn.Linear(self.enc_out_dim, self.latent_dim)
        self.fc_var = nn.Linear(self.enc_out_dim, self.latent_dim)



    def forward(self, x):
        x = self.encoder(x)
        mu = self.fc_mu(x)
        log_var = self.fc_var(x)
        _, _, z = self.sample(mu, log_var)
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

        x_enc = self.encoder(x)
        mu = self.fc_mu(x_enc)
        log_var = self.fc_var(x_enc)
        p, q, z = self.sample(mu, log_var)
        x_hat = self.decoder(z)

        recon_loss = F.mse_loss(x_hat, x, reduction="mean")

        kl = torch.distributions.kl_divergence(q, p)
        kl = kl.mean()
        kl *= self.kl_coeff

        loss = kl + recon_loss


        self.log(f'{stage}_recon_loss', recon_loss, on_epoch=True, on_step=True)
        self.log(f'{stage}_kl_loss', kl, on_epoch=True, on_step=True)
        self.log(f'{stage}_loss', loss, on_epoch=True, on_step=True, prog_bar=True)

        return loss

    def sample(self, mu, log_var):
        std = torch.exp(log_var / 2)
        p = torch.distributions.Normal(torch.zeros_like(mu), torch.ones_like(std))
        q = torch.distributions.Normal(mu, std)
        z = q.rsample()
        return p, q, z

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
    