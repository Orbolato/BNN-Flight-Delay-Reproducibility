"""Reproduce the BNN numerical experiment reported in the IEEE Access paper.

This script mirrors the archived executable implementation, including RNG-sensitive
model construction and Monte Carlo evaluation order.
"""

from pathlib import Path
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torchbnn as bnn

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler

SEED = 42
CANDIDATES = [
    Path("data/final_data_sbrf_sbgr.csv"),
    Path("../data/final_data_sbrf_sbgr.csv"),
]
CSV_PATH = next((p for p in CANDIDATES if p.exists()), CANDIDATES[0])

def reset_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

reset_seed()

print("CSV:", CSV_PATH)
print("PyTorch:", torch.__version__)
print("TorchBNN:", getattr(bnn, "__version__", "unknown"))
print("CUDA available:", torch.cuda.is_available())

raw = pd.read_csv(CSV_PATH)
print("Full preprocessed SBGR dataset:", raw.shape)

def prepare_source_dataframe(output_column):
    """Reproduce source preprocessing after the processed route data are loaded."""
    df = raw[raw["sg_icao_origem"] == 2].copy().reset_index(drop=True)
    df["flight_time_deviation_clipped"] = np.maximum(df["flight_time_deviation"], 0)
    df["arrival_delay_clipped"] = np.maximum(df["arrival_delay"], 0)

    alternate_outputs = [
        "flight_time_deviation",
        "flight_time_deviation_clipped",
        "arrival_delay",
        "arrival_delay_clipped",
    ]
    alternate_outputs.remove(output_column)
    for col in alternate_outputs:
        if col in df.columns:
            df = df.drop(columns=col)

    df = df.drop(columns=["sg_icao_origem", "tmi_duration", "rate_nm"])
    for col in list(df.columns):
        if col == output_column:
            continue
        if (df[col] == 0).all():
            df = df.drop(columns=col)

    cols = [c for c in df.columns if c != output_column] + [output_column]
    return df[cols]

for target in ["arrival_delay", "flight_time_deviation"]:
    d = prepare_source_dataframe(target)
    print("\n", target)
    print("  rows:", len(d))
    print("  input features:", d.shape[1] - 1)
    print("  mean:", round(d[target].mean(), 6))
    print("  std:", round(d[target].std(), 6))
    print("  min/max:", d[target].min(), d[target].max())
    print("  features:", list(d.columns[:-1]))

assert len(prepare_source_dataframe("arrival_delay")) == 14956
assert prepare_source_dataframe("arrival_delay").shape[1] - 1 == 23

def make_source_split_and_scaler(output_column):
    df = prepare_source_dataframe(output_column)
    x_full = df.iloc[:, :-1]
    y_full = df.iloc[:, -1]

    # IMPORTANT: this pre-shuffle exists in the original implementation.
    x_full, y_full = shuffle(x_full, y_full, random_state=SEED)

    x_main, x_test, y_main, y_test = train_test_split(
        x_full, y_full, train_size=0.8, shuffle=True, random_state=SEED
    )
    x_train, x_val, y_train, y_val = train_test_split(
        x_main, y_main, train_size=0.875, shuffle=True, random_state=SEED
    )

    y_train_original = y_train.to_numpy(copy=True)
    y_test_original = y_test.to_numpy(copy=True)

    # The source fits one column-wise MinMaxScaler to X and y together.
    scaler = MinMaxScaler()
    train_data = pd.concat([x_train, y_train], axis=1)
    scaled_train = pd.DataFrame(scaler.fit_transform(train_data), columns=train_data.columns)
    x_train_s = scaled_train.iloc[:, :-1]
    y_train_s = scaled_train.iloc[:, -1]

    test_data = pd.DataFrame(
        scaler.transform(pd.concat([x_test, y_test], axis=1)), columns=train_data.columns
    )
    x_test_s = test_data.iloc[:, :-1]
    y_test_s = test_data.iloc[:, -1]

    val_data = pd.DataFrame(
        scaler.transform(pd.concat([x_val, y_val], axis=1)), columns=train_data.columns
    )
    x_val_s = val_data.iloc[:, :-1]
    y_val_s = val_data.iloc[:, -1]

    return {
        "feature_names": list(x_full.columns),
        "scaler": scaler,
        "x_train": torch.tensor(x_train_s.values, dtype=torch.float32),
        "y_train": torch.tensor(y_train_s.values, dtype=torch.float32).unsqueeze(1),
        "x_val": torch.tensor(x_val_s.values, dtype=torch.float32),
        "y_val": torch.tensor(y_val_s.values, dtype=torch.float32).unsqueeze(1),
        "x_test": torch.tensor(x_test_s.values, dtype=torch.float32),
        "y_test": torch.tensor(y_test_s.values, dtype=torch.float32).unsqueeze(1),
        "y_train_original": y_train_original,
        "y_test_original": y_test_original,
    }

PAPER_CONFIGS = {
    "coverage": dict(n_hidden=128, learning_rate=1e-3, prior_sigma=1e-2, kl_constant=1e1),
    "loss": dict(n_hidden=256, learning_rate=5e-4, prior_sigma=1e-3, kl_constant=1e2),
}

def build_model_pair(n_features, cfg):
    # Match the archived source construction order exactly: BNN first, then ANN.
    bnn_model = nn.Sequential(
        bnn.BayesLinear(prior_mu=0, prior_sigma=cfg["prior_sigma"], in_features=n_features, out_features=cfg["n_hidden"]),
        nn.ReLU(),
        bnn.BayesLinear(prior_mu=0, prior_sigma=cfg["prior_sigma"], in_features=cfg["n_hidden"], out_features=cfg["n_hidden"]),
        nn.ReLU(),
        bnn.BayesLinear(prior_mu=0, prior_sigma=10 * cfg["prior_sigma"], in_features=cfg["n_hidden"], out_features=1),
    )
    # ANN initialization consumes PyTorch RNG values before BNN training in the source.
    ann_model = nn.Sequential(
        nn.Linear(n_features, cfg["n_hidden"], bias=True),
        nn.ReLU(),
        nn.Linear(cfg["n_hidden"], cfg["n_hidden"], bias=True),
        nn.ReLU(),
        nn.Linear(cfg["n_hidden"], 1, bias=True),
    )
    return bnn_model, ann_model

def make_scheduler(optimizer):
    try:
        return optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", factor=0.5, patience=200, verbose=True
        )
    except TypeError:
        return optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", factor=0.5, patience=200
        )

def train_bnn_source_exact(model, prep, cfg, n_epochs=10000, warmup_epochs=5000, log_every=500):
    """Reproduce the two-stage BNN training logic in the archived experiment."""
    x_train, y_train = prep["x_train"], prep["y_train"]
    x_val, y_val = prep["x_val"], prep["y_val"]

    optimizer = optim.Adam(model.parameters(), lr=cfg["learning_rate"])
    scheduler = make_scheduler(optimizer)
    mse_loss_fn = nn.MSELoss()
    kl_loss_fn = bnn.BKLLoss(reduction="mean", last_layer_only=False)
    final_kl_weight = cfg["kl_constant"] / len(x_train)

    mse_val_list = []
    best_val_loss = float("inf")
    patience_counter = 0
    patience = 1000

    for epoch in range(warmup_epochs):
        model.train()
        pred = model(x_train)
        mse = mse_loss_fn(pred, y_train)
        kl = kl_loss_fn(model)
        loss = mse

        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        model.eval()
        with torch.no_grad():
            pred_val = model(x_val)
            mse_val = mse_loss_fn(pred_val, y_val)
            scheduler.step(mse_val)
            mse_val_list.append(mse_val)

        if epoch % log_every == 0:
            print(f"Warm {epoch:5d} | MSE={mse.item():.6f} | KL={kl.item():.6f} | Val={mse_val.item():.6f}")

        if mse_val.item() < best_val_loss:
            best_val_loss = mse_val.item()
            patience_counter = 0
            best_state = model.state_dict().copy()
        else:
            patience_counter += 1

        if patience_counter >= patience:
            print(f"Warm-start early stopping at epoch {epoch}")
            break

    final_epoch = epoch
    model.load_state_dict(best_state)

    for epoch in range(final_epoch, n_epochs):
        model.train()
        progress = (epoch - final_epoch) / (n_epochs - final_epoch)
        kl_weight = final_kl_weight * progress

        pred = model(x_train)
        mse = mse_loss_fn(pred, y_train)
        kl = kl_loss_fn(model)
        loss = mse + kl_weight * kl

        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        model.eval()
        with torch.no_grad():
            pred_val = model(x_val)
            mse_val = mse_loss_fn(pred_val, y_val)
            scheduler.step(mse_val)
            mse_val_list.append(mse_val)

        if epoch % log_every == 0:
            print(f"BNN  {epoch:5d} | MSE={mse.item():.6f} | KL={kl.item():.6f} | wKL={kl_weight:.3e} | Val={mse_val.item():.6f}")

    return model, mse_val_list

def evaluate_bnn_source_exact(model, prep, n_mc=1000):
    """Match the archived stochastic evaluation sequence exactly."""
    x_train = prep["x_train"]
    x_test = prep["x_test"]
    y_test = prep["y_test"]
    y_test_original = prep["y_test_original"]
    scaler = prep["scaler"]

    model.eval()
    with torch.no_grad():
        _train_samples = np.array([model(x_train).detach().numpy() for _ in range(n_mc)])

    mse_loss = nn.MSELoss()
    mse_mean = 0.0
    with torch.no_grad():
        for _ in range(n_mc):
            pred = model(x_test)
            mse_mean += mse_loss(pred, y_test).item()
    mse_mean /= n_mc

    with torch.no_grad():
        test_samples = np.array([model(x_test).detach().numpy() for _ in range(n_mc)])
    test_samples = test_samples[:, :, 0].T

    y_min = scaler.data_min_[-1]
    y_max = scaler.data_max_[-1]
    samples_unscaled = y_min + test_samples * (y_max - y_min)
    mean_values = samples_unscaled.mean(axis=1)
    std_values = samples_unscaled.std(axis=1)

    mse_unscaled = np.mean((mean_values - y_test_original) ** 2)
    mae = np.mean(np.abs(mean_values - y_test_original))
    coverage_95 = np.mean(
        (y_test_original >= mean_values - 2.0 * std_values)
        & (y_test_original <= mean_values + 2.0 * std_values)
    )

    return {
        "test_mse_scaled": mse_mean,
        "test_mse_unscaled": mse_unscaled,
        "test_mae_min": mae,
        "coverage_95": coverage_95,
        "mean_uncertainty_sigma_min": std_values.mean(),
        "mean_prediction": mean_values,
        "std_prediction": std_values,
    }

PAPER_BENCHMARK = {
    ("arrival_delay", "loss"): {"mae": 6.45, "coverage": 0.360},
    ("arrival_delay", "coverage"): {"mae": 6.68, "coverage": 0.973},
    ("flight_time_deviation", "loss"): {"mae": 6.31, "coverage": 0.322},
    ("flight_time_deviation", "coverage"): {"mae": 6.44, "coverage": 0.947},
}

RUNS = [
    ("arrival_delay", "coverage"),
    # ("arrival_delay", "loss"),
    # ("flight_time_deviation", "coverage"),
    # ("flight_time_deviation", "loss"),
]

results = {}
models = {}
for target, model_type in RUNS:
    print("\n" + "=" * 80)
    print(target, "/", model_type)
    print("=" * 80)
    reset_seed()

    prep = make_source_split_and_scaler(target)
    cfg = PAPER_CONFIGS[model_type]
    model, _ann_model = build_model_pair(len(prep["feature_names"]), cfg)
    model, history = train_bnn_source_exact(model, prep, cfg)
    result = evaluate_bnn_source_exact(model, prep, n_mc=1000)

    expected = PAPER_BENCHMARK[(target, model_type)]
    print("\nRESULT")
    print(f"  scaled test MSE: {result['test_mse_scaled']:.6g}")
    print(f"  test MAE:        {result['test_mae_min']:.3f} min")
    print(f"  95% coverage:    {100*result['coverage_95']:.2f}%")
    print(f"  mean sigma:      {result['mean_uncertainty_sigma_min']:.3f} min")
    print("\nPAPER BENCHMARK")
    print(f"  test MAE:        {expected['mae']:.2f} min")
    print(f"  95% coverage:    {100*expected['coverage']:.1f}%")

    models[(target, model_type)] = model
    results[(target, model_type)] = result
