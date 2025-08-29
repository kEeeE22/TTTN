import torch
import matplotlib.pyplot as plt
import io, base64

device = 'cpu'

def predict_(
    model, 
    x_sample: torch.Tensor,   # đầu vào bắt buộc là tensor
    threshold: float = 0.01, 
    flat: bool = True, 
    device: str = 'cpu', 
    visualize: bool = False
):
    model.eval()
    with torch.no_grad():
        if flat:
            x = x_sample.view(1, -1).to(device)  # reshape phẳng
        else:
            x = x_sample.unsqueeze(0).to(device)  # giữ nguyên theo chuỗi

        x_hat = model(x)

        # Tính MSE reconstruction error
        err = torch.mean((x_hat - x) ** 2).item()
        pred = int(err > threshold)   # 1 = bất thường, 0 = bình thường

    img_base64 = None
    if visualize:
        W, F = x_sample.shape
        if flat:
            x_np = x.view(W, F).cpu().numpy()
            x_hat_np = x_hat.view(W, F).cpu().numpy()
        else:
            x_np = x.squeeze(0).cpu().numpy()
            x_hat_np = x_hat.squeeze(0).cpu().numpy()

        fig, axes = plt.subplots(F, 1, figsize=(10, 2.5*F))
        if F == 1:  
            axes = [axes]

        for f in range(F):
            axes[f].plot(x_np[:, f], label="Original")
            axes[f].plot(x_hat_np[:, f], linestyle="--", label="Reconstructed")
            axes[f].set_title(f"LƯU LƯỢNG TỨC THỜI")
            axes[f].legend()

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig)

    return pred, err, img_base64


def preprocess_(sample_df, feature, scaler):
    features_data = sample_df[feature].values
    features_scaled = scaler.transform(features_data)
    return features_scaled