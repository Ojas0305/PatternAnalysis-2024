import torch
import torch.nn as nn

class MappingNetwork(nn.Module):
    def __init__(self, z_dim, w_dim):
        super().__init__()
        self.mapping = nn.Sequential(
            nn.Linear(z_dim, w_dim),
            nn.ReLU(),
            nn.Linear(w_dim, w_dim)
        )
    
    def forward(self, z):
        return self.mapping(z)

class StyleGANGenerator(nn.Module):
    def __init__(self, z_dim, w_dim, img_channels):
        super().__init__()
        self.mapping = MappingNetwork(z_dim, w_dim)
        self.synthesis = nn.Sequential(
            nn.ConvTranspose2d(w_dim, 256, kernel_size=4, stride=1, padding=0),
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, img_channels, kernel_size=4, stride=2, padding=1),
            nn.Tanh()
        )

    def forward(self, z):
        w = self.mapping(z)
        w = w.view(w.size(0), -1, 1, 1)
        generated_image = self.synthesis(w)
        return generated_image
    
    @staticmethod
    def generator_loss(fake_output):
        return torch.mean((fake_output - 1) ** 2)

class StyleGANDiscriminator(nn.Module):
    def __init__(self, img_channels):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(img_channels, 128, kernel_size=4, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.Flatten(),
            nn.Linear(256 * 32 * 32, 1)
        )

    def forward(self, img):
        return self.model(img)
    
    @staticmethod
    def discriminator_loss(real_output, fake_output):
        real_loss = torch.mean((real_output - 1) ** 2)
        fake_loss = torch.mean(fake_output ** 2)
        return (real_loss + fake_loss) / 2
    
if __name__ == "__main__":
    z_dim = 128  
    w_dim = 512  
    img_channels = 3  

    generator = StyleGANGenerator(z_dim=z_dim, w_dim=w_dim, img_channels=img_channels)

    generator.eval()

    z = torch.randn(1, z_dim) 

    with torch.no_grad():
        generated_image = generator(z)
        
    print(f"Output shape: {generated_image.shape}")