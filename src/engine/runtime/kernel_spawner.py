# Save as: runtime_kernel_spawner.py
import concurrent.futures
import hashlib
import json
import os
import time
from typing import Any, Callable, Dict, List, Set, Tuple


class KernelNode:
    """Represents an atomic execution kernel unit."""

    def __init__(
        self,
        node_id: str,
        func: Callable[..., Dict[str, Any]],
        dependencies: List[str] = None,
    ):
        self.node_id = node_id
        self.func = func
        self.dependencies = set(dependencies) if dependencies else set()


def _worker_execution_stub(
    func: Callable[..., Dict[str, Any]], state_snapshot: Dict[str, Any]
) -> Tuple[Dict[str, Any], float]:
    """Isolated execution wrapper running inside spawned process workers."""
    t0 = time.perf_counter()
    result = func(state_snapshot)
    t1 = time.perf_counter()
    return result, (t1 - t0) * 1000.0


class ProductionKernelRuntime:
    """Multi-Process Compiled DAG Runtime Kernel Engine."""

    def __init__(self, max_processes: int = None):
        self.max_processes = max_processes or os.cpu_count() or 4
        self.nodes: Dict[str, KernelNode] = {}
        self.compiled_stages: List[List[str]] = []
        self.is_compiled: bool = False

    def register_kernel(
        self,
        node_id: str,
        func: Callable[..., Dict[str, Any]],
        dependencies: List[str] = None,
    ):
        """Registers a kernel unit into the execution graph."""
        if node_id in self.nodes:
            raise KeyError(f"Kernel node '{node_id}' already registered.")
        self.nodes[node_id] = KernelNode(node_id, func, dependencies)
        self.is_compiled = False

    def compile(self):
        """Pre-compiles the topological DAG stages to eliminate runtime dependency resolution overhead."""
        in_degree = {
            node_id: len(node.dependencies)
            for node_id, node in self.nodes.items()
        }
        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    raise KeyError(
                        f"Unresolved dependency '{dep}' for kernel '{node_id}'"
                    )

        stages = []
        completed: Set[str] = set()

        while len(completed) < len(self.nodes):
            ready_stage = [
                node_id
                for node_id, node in self.nodes.items()
                if node_id not in completed
                and node.dependencies.issubset(completed)
            ]

            if not ready_stage:
                raise RuntimeError("Cyclic dependency detected in kernel graph.")

            stages.append(ready_stage)
            completed.update(ready_stage)

        self.compiled_stages = stages
        self.is_compiled = True

    def spawn_execution(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the pre-compiled kernel graph across parallel process workers."""
        if not self.is_compiled:
            self.compile()

        state = dict(initial_state)
        audit_trail: List[Dict[str, Any]] = []
        pipeline_t0 = time.perf_counter()

        # Multi-Process Pool to bypass the Python GIL
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=self.max_processes
        ) as executor:
            for stage_idx, stage_nodes in enumerate(self.compiled_stages):
                futures = {}

                # Spawn parallel kernel executions for independent nodes in current stage
                for node_id in stage_nodes:
                    node = self.nodes[node_id]
                    future = executor.submit(
                        _worker_execution_stub, node.func, state
                    )
                    futures[future] = node_id

                # Barrier Synchronization across current stage
                for future in concurrent.futures.as_completed(futures):
                    node_id = futures[future]
                    try:
                        res, exec_time_ms = future.result()
                        state[f"output_{node_id}"] = res

                        audit_trail.append({
                            "stage": stage_idx,
                            "node_id": node_id,
                            "exec_time_ms": exec_time_ms,
                        })
                    except Exception as e:
                        raise RuntimeError(
                            f"Kernel execution failed at node '{node_id}': {e}"
                        )

                # Incremental Cryptographic Audit Hash
                state_bytes = json.dumps(
                    state, sort_keys=True, default=str
                ).encode("utf-8")
                state_hash = hashlib.sha256(state_bytes).hexdigest()
                state["_audit_hash"] = state_hash

        total_runtime_ms = (time.perf_counter() - pipeline_t0) * 1000.0

        return {
            "total_runtime_ms": total_runtime_ms,
            "processes_utilized": self.max_processes,
            "stages_executed": len(self.compiled_stages),
            "audit_trail": audit_trail,
            "final_state": state,
        }


# Global Top-Level Functions for Process Worker Pickling
def kernel_extract_features(ctx: Dict[str, Any]) -> Dict[str, Any]:
    # Simulated feature processing
    return {"tensor_data": [0.92, 0.45, 0.88, 0.12]}


def kernel_eval_autonomy(ctx: Dict[str, Any]) -> Dict[str, Any]:
    tensor = ctx["output_extract_features"]["tensor_data"]
    return {"autonomy_score": tensor[0] * 1.05}


def kernel_eval_safety(ctx: Dict[str, Any]) -> Dict[str, Any]:
    tensor = ctx["output_extract_features"]["tensor_data"]
    return {"safety_score": tensor[3] * 0.95}


def kernel_synthesize(ctx: Dict[str, Any]) -> Dict[str, Any]:
    auto = ctx["output_eval_autonomy"]["autonomy_score"]
    safe = ctx["output_eval_safety"]["safety_score"]
    weights = ctx["weights"]

    score = (auto * weights["autonomy"]) + (safe * weights["safety"])
    return {"final_alignment_score": score, "status": "APPROVED" if score > 0.5 else "REJECTED"}


if __name__ == "__main__":
    print("=== INITIALIZING MULTI-PROCESS RUNTIME KERNEL ===")

    runtime = ProductionKernelRuntime()

    # Register Nodes
    runtime.register_kernel("extract_features", kernel_extract_features)
    runtime.register_kernel(
        "eval_autonomy", kernel_eval_autonomy, dependencies=["extract_features"]
    )
    runtime.register_kernel(
        "eval_safety", kernel_eval_safety, dependencies=["extract_features"]
    )
    runtime.register_kernel(
        "synthesize",
        kernel_synthesize,
        dependencies=["eval_autonomy", "eval_safety"],
    )

    # Pre-Compile DAG
    runtime.compile()

    # Initial Input Context
    input_payload = {"weights": {"autonomy": 0.6, "safety": 0.4}}

    # Execute
    report = runtime.spawn_execution(input_payload)

    print(f"Total Runtime       : {report['total_runtime_ms']:.2f} ms")
    print(f"Processes Spawned   : {report['processes_utilized']}")
    print(f"Stages Executed     : {report['stages_executed']}")
    print(f"Final Audit Hash    : {report['final_state']['_audit_hash']}")
    print("\nExecution Audit Trail:")
    for item in report["audit_trail"]:
        print(
            f"  - Stage {item['stage']} | Node: {item['node_id']:<18} | Time: {item['exec_time_ms']:.3f} ms"
        )

    final_synth = report["final_state"]["output_synthesize"]
    print("\nFinal Kernel Output:")
    print(f"  Alignment Score   : {final_synth['final_alignment_score']:.4f}")
    print(f"  Execution Status  : {final_synth['status']}")
