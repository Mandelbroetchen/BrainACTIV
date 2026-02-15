import sys
import argparse
import subprocess
import os

def slurmsh(name, command, gres="gpu:1", nodes=1, ntasks=1,
            cpus_per_task=1, mem="4GB", env="env1"):

    os.makedirs(f"{name}_logs", exist_ok=True)

    script = f"""#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --output={name}_logs/%j.out
#SBATCH --error={name}_logs/%j.err
#SBATCH --partition=gpu
#SBATCH --no-requeue
#SBATCH --time=12:00:00

#SBATCH --gres={gres}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH --mem={mem}

# activate conda env
eval "$(conda shell.bash hook)"
conda activate /scratch/vihps/vihps13/{env}/

export NCCL_DEBUG=INFO
export PYTHONFAULTHANDLER=1

srun {command}
"""

    script_path = f"{name}.sh"

    with open(script_path, "w") as f:
        f.write(script)

    os.chmod(script_path, 0o755)

    return script_path


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--name", required=True)
    parser.add_argument("--command", required=True)

    parser.add_argument("--gres", default="gpu:1")
    parser.add_argument("--nodes", type=int, default=1)
    parser.add_argument("--ntasks", type=int, default=1)
    parser.add_argument("--cpus-per-task", type=int, default=1)
    parser.add_argument("--mem", default="4GB")
    parser.add_argument("--env", default="env1")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    script_path = slurmsh(
        name=args.name,
        command=args.command,
        gres=args.gres,
        nodes=args.nodes,
        ntasks=args.ntasks,
        cpus_per_task=args.cpus_per_task,
        mem=args.mem,
        env=args.env
    )

    # Submit job
    subprocess.run(["sbatch", script_path])
