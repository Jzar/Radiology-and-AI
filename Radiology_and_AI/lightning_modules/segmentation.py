#@title LightningModule, this is supposed to be in LightningModules but I put it here for easy modification
#Pytorch-lightning setup
import sys
sys.path.append('../')
from lib.medzoo.Unet3D import UNet3D
from lib.losses3D.basic import compute_per_channel_dice, expand_as_one_hot
import torch
import pytorch_lightning as pl

class TumourSegmentation(pl.LightningModule):
  def __init__(self, learning_rate, collator, batch_size, train_dataset, eval_dataset):
    super().__init__()
    self.model =  UNet3D(in_channels=4, n_classes=3, base_n_filter=8) #.cuda()
    self.learning_rate = learning_rate
    self.collator = collator
    self.batch_size = batch_size
    self.train_dataset = train_dataset
    self.eval_dataset = eval_dataset
    self.save_hyperparameters()

  def forward(self,x):
  #  x=x.half()

    f = self.model.forward(x)

  #  print('Done forward step!')
    return f

  def training_step(self, batch, batch_idx):
    x, y = batch
    x = torch.unsqueeze(x, axis=0)
    y = torch.unsqueeze(y, axis=0)
    #print(x.shape)

    y_hat = self.forward(x)

    #plt.imshow(y_hat[0, 0, 120], cmap='')
    #plt.imshow(y_hat.cpu()[0, 1, 120])
    #plt.imshow(y_hat[0, 2, 120])
    #plt.imshow(y_hat[0, 3, 120])
    #plt.show()

    shape = list(y.size())
    shape[1] = 3
    zeros = torch.zeros(shape).cuda()

    zeros[:, 0][torch.squeeze(y == 1, dim=1)] = 1
    zeros[:, 1][torch.squeeze(y == 4, dim=1)] = 1
    zeros[:, 2][torch.squeeze(y == 2, dim=1)] = 1

  # basic mean of all channels for now
  
    loss = -1*compute_per_channel_dice(y_hat, zeros)
    loss[loss != loss] = 0
    self.log('train_loss_core', loss[0], on_step=True, on_epoch=True, prog_bar=True, logger=True)
    self.log('train_loss_enhancing', loss[1], on_step=True, on_epoch=True, prog_bar=True, logger=True)
    self.log('train_loss_edema', loss[2], on_step=True, on_epoch=True, prog_bar=True, logger=True)
    loss = torch.sum(loss)

    #self.logger.experiment.flush()

    return loss

  def validation_step(self, batch, batch_idx):
    x, y = batch
    x = torch.unsqueeze(x, axis=0)
    y = torch.unsqueeze(y, axis=0)
    #print(x.shape)

    y_hat = self.forward(x)

    #plt.imshow(y_hat[0, 0, 120], cmap='')
    #plt.imshow(y_hat.cpu()[0, 1, 120])
    #plt.imshow(y_hat[0, 2, 120])
    #plt.imshow(y_hat[0, 3, 120])
    #plt.show()

    shape = list(y.size())
    shape[1] = 3
    zeros = torch.zeros(shape).cuda()

    zeros[:, 0][torch.squeeze(y == 1, dim=1)] = 1
    zeros[:, 1][torch.squeeze(y == 4, dim=1)] = 1
    zeros[:, 2][torch.squeeze(y == 2, dim=1)] = 1

  # basic mean of all channels for now
    loss = -1*compute_per_channel_dice(y_hat, zeros)
    loss[loss != loss] = 0
    self.log('test_loss_core', loss[0], on_step=True, on_epoch=True, prog_bar=True, logger=True)
    self.log('test_loss_enhancing', loss[1], on_step=True, on_epoch=True, prog_bar=True, logger=True)
    self.log('test_loss_edema', loss[2], on_step=True, on_epoch=True, prog_bar=True, logger=True)
    loss = torch.sum(loss)
    return loss
  def train_dataloader(self):
      return torch.utils.data.DataLoader(self.train_dataset, batch_size=self.batch_size,collate_fn=self.collator)
  def val_dataloader(self):
      return torch.utils.data.DataLoader(self.eval_dataset, batch_size=self.batch_size,collate_fn=self.collator)      

  def train_dataloader(self):
      return torch.utils.data.DataLoader(self.train_dataset, batch_size=self.batch_size,collate_fn=self.collator)
  def val_dataloader(self):
      return torch.utils.data.DataLoader(self.eval_dataset, batch_size=self.batch_size,collate_fn=self.collator)      

  def configure_optimizers(self):
      return torch.optim.Adam(self.parameters(), lr=self.learning_rate)
