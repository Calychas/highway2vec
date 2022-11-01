import torch
from torch import nn
from torch import optim
import torch.nn.functional as F
import pytorch_lightning as pl


class LitAutoEncoder(pl.LightningModule):
    def __init__(self, in_dim: int, hidden_dim: int = 64, latent_dim: int = 3, lr: float = 1e-3):
        super().__init__()

        self.save_hyperparameters()

        self.encoder = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
            # nn.Tanh()
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
        # loss = F.binary_cross_entropy_with_logits(x_hat, x)

        self.log(f'{stage}_loss', loss, on_epoch=True, on_step=True, prog_bar=True)

        return loss

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=self.lr)
        return optimizer
