using System;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Security
{
    public interface IInternalProbeTestSurface
    {
        PipelineProbeResult ExecuteInternalProbe(PipelineProbeRequest request);
        bool TryInvokeFromGameplayTransport(string transportType, object packet, out string rejectionReason);
    }

    public class InternalProbeTestSurface : IInternalProbeTestSurface
    {
        private readonly IPipelineTransactionCoordinator _coordinator;

        public InternalProbeTestSurface(IPipelineTransactionCoordinator coordinator)
        {
            _coordinator = coordinator;
        }

        public PipelineProbeResult ExecuteInternalProbe(PipelineProbeRequest request)
        {
            // Internal local execution only
            return _coordinator.ExecuteProbeCas(request);
        }

        public bool TryInvokeFromGameplayTransport(string transportType, object packet, out string rejectionReason)
        {
            // Unconditional rejection: PIPELINE_PROBE_CAS is strictly an internal administrative probe
            // and must never be reachable over client gameplay network transports.
            rejectionReason = $"ACCESS_DENIED: Operation 'PIPELINE_PROBE_CAS' is an internal administrative probe and cannot be invoked over gameplay transport '{transportType}'.";
            return false;
        }
    }
}
