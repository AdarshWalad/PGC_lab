"""
plot_graphs.py

Generates visualization charts for Experiment 4 (Cache Coherence,
False Sharing, and NUMA Effects) from the observed experimental outputs.
Saves PNG figures into ../graphs/.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Output directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPHS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "graphs"))
os.makedirs(GRAPHS_DIR, exist_ok=True)

# Global styling
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#fafafa",
    "axes.edgecolor": "#cccccc",
    "axes.grid": True,
    "grid.color": "#e0e0e0",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
})


def add_bar_labels(ax, rects, fmt="{:.0f}", fontsize=8.5, offset=3):
    """Attach a text label above each bar displaying its height."""
    for rect in rects:
        h = rect.get_height()
        ax.annotate(
            fmt.format(h),
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, offset),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=fontsize,
            fontweight="normal",
        )


def plot_coherence_sim():
    """Graph 1: MSI vs MESI vs MOESI Cache Coherence Metrics (1000 iterations)."""
    protocols = ["MSI", "MESI", "MOESI"]

    # Observed totals for adjacent layout (1000 iterations)
    metrics = {
        "Bus Transactions": [4000, 3999, 3999],
        "BusRd": [2000, 2000, 2000],
        "BusUpgr": [2000, 1999, 1999],
        "Invalidations": [1999, 1999, 1999],
        "Writebacks": [1999, 1999, 0],
        "Cache-to-Cache (C2C)": [0, 0, 1999],
    }

    padded_bus_tx = [4, 2, 2]
    adj_bus_tx = [4000, 3999, 3999]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios": [1.8, 1]}
    )

    # Panel A: Detailed metrics for Adjacent layout
    x = np.arange(len(protocols))
    width = 0.13
    colors = ["#2563eb", "#0891b2", "#7c3aed", "#d97706", "#dc2626", "#16a34a"]

    for i, (label, values) in enumerate(metrics.items()):
        offset = (i - (len(metrics) - 1) / 2) * width
        rects = ax1.bar(x + offset, values, width, label=label, color=colors[i], edgecolor="white")
        add_bar_labels(ax1, rects, fmt="{:.0f}", fontsize=7.5)

    ax1.set_title("Adjacent Layout: Protocol Traffic Breakdown (1000 Iterations)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(protocols, fontweight="bold")
    ax1.set_ylabel("Event Count")
    ax1.set_ylim(0, 5100)
    ax1.legend(loc="upper right", ncol=2, fontsize=8.5, framealpha=0.95)

    # Panel B: Adjacent vs Padded Total Bus Transactions
    w2 = 0.34
    r1 = ax2.bar(x - w2 / 2, adj_bus_tx, w2, label="Adjacent (False Sharing)", color="#dc2626", edgecolor="white")
    r2 = ax2.bar(x + w2 / 2, padded_bus_tx, w2, label="Padded (No Contention)", color="#16a34a", edgecolor="white")

    add_bar_labels(ax2, r1, fmt="{:.0f}", fontsize=9)
    add_bar_labels(ax2, r2, fmt="{:.0f}", fontsize=9)

    ax2.set_title("Adjacent vs. Padded: Total Bus Transactions")
    ax2.set_xticks(x)
    ax2.set_xticklabels(protocols, fontweight="bold")
    ax2.set_ylabel("Total Bus Transactions")
    ax2.set_ylim(0, 5100)
    ax2.legend(loc="upper right", fontsize=9, framealpha=0.95)

    fig.suptitle(
        "Experiment 4.1: Cache Coherence Simulation (coherence_sim.py)",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout()
    out_path = os.path.join(GRAPHS_DIR, "graph1_coherence_protocols.png")
    plt.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_false_sharing():
    """Graph 2: False Sharing Benchmark (false_sharing.c & compare_numa.c)."""
    # Data from false_sharing.c (threads = 2, 4)
    fs_threads = np.array([2, 4])
    fs_adj = [0.3925, 1.4164]
    fs_pad = [0.0326, 0.0216]
    fs_speedup = [a / p for a, p in zip(fs_adj, fs_pad)]

    # Data from compare_numa.c default run (threads = 1, 2, 4)
    cn_threads = np.array([1, 2, 4])
    cn_adj = [0.0351, 0.4215, 1.4088]
    cn_pad = [0.0399, 0.0293, 0.0119]
    cn_speedup = [a / p for a, p in zip(cn_adj, cn_pad)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.2))

    # Panel A: Execution Time vs Thread Count
    x = np.arange(len(cn_threads))
    w = 0.32
    r1 = ax1.bar(x - w / 2, cn_adj, w, label="Adjacent (False Sharing)", color="#ef4444", edgecolor="white")
    r2 = ax1.bar(x + w / 2, cn_pad, w, label="Padded (64B Cache-Line Aligned)", color="#10b981", edgecolor="white")

    # Overlay standalone false_sharing.c markers for 2 & 4 threads
    ax1.scatter([1 - w / 2, 2 - w / 2], fs_adj, color="#7f1d1d", marker="D", s=45, zorder=5, label="false_sharing.c (Adjacent)")
    ax1.scatter([1 + w / 2, 2 + w / 2], fs_pad, color="#064e3b", marker="o", s=45, zorder=5, label="false_sharing.c (Padded)")

    add_bar_labels(ax1, r1, fmt="{:.4f}s", fontsize=8.5)
    add_bar_labels(ax1, r2, fmt="{:.4f}s", fontsize=8.5)

    ax1.set_title("Execution Time: Adjacent vs. Padded (100M Increments)")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{t} Thread{'s' if t > 1 else ''}" for t in cn_threads], fontweight="bold")
    ax1.set_ylabel("Execution Time (seconds)")
    ax1.set_ylim(0, 1.65)
    ax1.legend(loc="upper left", fontsize=8.5, framealpha=0.95)

    # Panel B: Speedup Factor from Cache-Line Padding
    r_sp1 = ax2.bar(x - w / 2, cn_speedup, w, label="compare_numa.c Speedup", color="#3b82f6", edgecolor="white")
    r_sp2 = ax2.bar(np.array([1, 2]) + w / 2, fs_speedup, w, label="false_sharing.c Speedup", color="#8b5cf6", edgecolor="white")

    add_bar_labels(ax2, r_sp1, fmt="{:.1f}x", fontsize=9)
    add_bar_labels(ax2, r_sp2, fmt="{:.1f}x", fontsize=9)

    ax2.axhline(1.0, color="#6b7280", linestyle=":", linewidth=1.2, label="1.0x Baseline (No Speedup)")
    ax2.set_title("Speedup Gained by Eliminating False Sharing")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{t} Thread{'s' if t > 1 else ''}" for t in cn_threads], fontweight="bold")
    ax2.set_ylabel("Speedup (Adjacent Time / Padded Time)")
    ax2.set_ylim(0, 138)
    ax2.legend(loc="upper left", fontsize=8.5, framealpha=0.95)

    fig.suptitle(
        "Experiment 4.2: False Sharing Impact & Cache-Line Padding",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout()
    out_path = os.path.join(GRAPHS_DIR, "graph2_false_sharing.png")
    plt.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_numa_sweep():
    """Graph 3: NUMA Memory Bandwidth Sweep (numa_sweep.c, 512 MB x 4 passes = 2 GB)."""
    configs = [
        "2 Threads\n(Default OS)",
        "2 Threads\n(Pinned Local NUMA\ncpunode=0, mem=0)",
        "12 Threads\n(Default, Run 1)",
        "12 Threads\n(512 MB, Run 2)",
    ]
    times = [0.2511, 0.0834, 0.0932, 0.0803]
    # Total data read: 512 MB * 4 passes = 2048 MB = 2.0 GB
    total_gb = (512 * 4) / 1024.0
    bandwidth_gbs = [total_gb / t for t in times]

    colors = ["#f59e0b", "#10b981", "#3b82f6", "#2563eb"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.2))
    x = np.arange(len(configs))
    w = 0.52

    r1 = ax1.bar(x, times, w, color=colors, edgecolor="white")
    add_bar_labels(ax1, r1, fmt="{:.4f} s", fontsize=9)
    ax1.set_title("Sweep Execution Time (Lower is Better)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(configs, fontsize=8.5)
    ax1.set_ylabel("Execution Time (seconds)")
    ax1.set_ylim(0, 0.295)

    r2 = ax2.bar(x, bandwidth_gbs, w, color=colors, edgecolor="white")
    add_bar_labels(ax2, r2, fmt="{:.2f} GB/s", fontsize=9)
    ax2.set_title("Effective Memory Bandwidth (Higher is Better)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(configs, fontsize=8.5)
    ax2.set_ylabel("Throughput (GB/s)")
    ax2.set_ylim(0, 30)

    fig.suptitle(
        "Experiment 4.3: NUMA Memory Sweep (numa_sweep.c — 512 MB Buffer, 4 Passes)",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout()
    out_path = os.path.join(GRAPHS_DIR, "graph3_numa_sweep.png")
    plt.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_compare_numa():
    """Graph 4: Default vs NUMA-Pinned Comparison (compare_numa.c)."""
    threads = [1, 2, 4]

    # Table 1: False sharing
    def_adj = [0.0351, 0.4215, 1.4088]
    def_pad = [0.0399, 0.0293, 0.0119]
    pin_adj = [0.0350, 0.4377, 1.3523]
    pin_pad = [0.0391, 0.0362, 0.0128]

    # Table 2: Memory sweep (512 MB, 4 passes)
    sweep_threads = [1, 2]
    sweep_def = [0.1192, 0.0873]
    sweep_pin = [0.1043, 0.0842]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14, 5.2), gridspec_kw={"width_ratios": [1.5, 1]}
    )

    # Panel A: Table 1 comparison
    x = np.arange(len(threads))
    w = 0.19
    r1 = ax1.bar(x - 1.5 * w, def_adj, w, label="Default — Adjacent", color="#ef4444", edgecolor="white")
    r2 = ax1.bar(x - 0.5 * w, pin_adj, w, label="NUMA Node 0 — Adjacent", color="#f97316", edgecolor="white")
    r3 = ax1.bar(x + 0.5 * w, def_pad, w, label="Default — Padded", color="#10b981", edgecolor="white")
    r4 = ax1.bar(x + 1.5 * w, pin_pad, w, label="NUMA Node 0 — Padded", color="#06b6d4", edgecolor="white")

    add_bar_labels(ax1, r1, fmt="{:.3f}", fontsize=7.5)
    add_bar_labels(ax1, r2, fmt="{:.3f}", fontsize=7.5)
    add_bar_labels(ax1, r3, fmt="{:.3f}", fontsize=7.5)
    add_bar_labels(ax1, r4, fmt="{:.3f}", fontsize=7.5)

    ax1.set_title("Table 1: False Sharing (Default vs. Local NUMA Binding)")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{t} Thread{'s' if t > 1 else ''}" for t in threads], fontweight="bold")
    ax1.set_ylabel("Execution Time (seconds)")
    ax1.set_ylim(0, 1.65)
    ax1.legend(loc="upper left", fontsize=8.5, framealpha=0.95)

    # Panel B: Table 2 comparison
    x2 = np.arange(len(sweep_threads))
    w2 = 0.30
    rs1 = ax2.bar(x2 - w2 / 2, sweep_def, w2, label="Default (./compare_numa)", color="#6366f1", edgecolor="white")
    rs2 = ax2.bar(x2 + w2 / 2, sweep_pin, w2, label="Local NUMA (node 0)", color="#0ea5e9", edgecolor="white")

    add_bar_labels(ax2, rs1, fmt="{:.4f}s", fontsize=9)
    add_bar_labels(ax2, rs2, fmt="{:.4f}s", fontsize=9)

    ax2.set_title("Table 2: 512 MB Memory Sweep (4 Passes)")
    ax2.set_xticks(x2)
    ax2.set_xticklabels([f"{t} Thread{'s' if t > 1 else ''}" for t in sweep_threads], fontweight="bold")
    ax2.set_ylabel("Execution Time (seconds)")
    ax2.set_ylim(0, 0.145)
    ax2.legend(loc="upper right", fontsize=8.5, framealpha=0.95)

    fig.suptitle(
        "Experiment 4.4: Default Scheduling vs. NUMA Local Binding (compare_numa.c)",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout()
    out_path = os.path.join(GRAPHS_DIR, "graph4_compare_numa.png")
    plt.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    plot_coherence_sim()
    plot_false_sharing()
    plot_numa_sweep()
    plot_compare_numa()
    print("All graphs generated successfully.")
