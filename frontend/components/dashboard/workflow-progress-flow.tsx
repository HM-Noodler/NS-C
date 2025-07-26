import { WorkflowStage } from "@/types";

interface WorkflowProgressFlowProps {
  stages: WorkflowStage[];
  currentStage: string;
}

export function WorkflowProgressFlow({ stages, currentStage }: WorkflowProgressFlowProps) {
  return (
    <div className="flex items-center justify-between w-full max-w-4xl mx-auto mb-8">
      {stages.map((stage, index) => (
        <div key={stage.id} className="flex items-center">
          <div className="flex flex-col items-center">
            <div
              className={`w-16 h-16 rounded-full border-4 flex items-center justify-center transition-all duration-300 ${
                stage.status === 'completed'
                  ? 'bg-green-50 border-green-500'
                  : stage.status === 'current'
                  ? 'bg-blue-50 border-blue-500'
                  : 'bg-gray-50 border-gray-300'
              }`}
            >
              {stage.status === 'completed' ? (
                <svg
                  className="w-8 h-8 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : stage.status === 'current' ? (
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              ) : (
                <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
              )}
            </div>
            
            <div className="mt-3 text-center">
              <div
                className={`text-sm font-medium ${
                  stage.status === 'completed'
                    ? 'text-green-600'
                    : stage.status === 'current'
                    ? 'text-blue-600'
                    : 'text-gray-500'
                }`}
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
              >
                {stage.name}
              </div>
              <div
                className={`text-xs mt-1 ${
                  stage.status === 'completed'
                    ? 'text-green-500'
                    : stage.status === 'current'
                    ? 'text-blue-500'
                    : 'text-gray-400'
                }`}
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
              >
                Day {stage.day}
              </div>
            </div>
          </div>
          
          {index < stages.length - 1 && (
            <div className="flex-1 mx-4">
              <svg
                className="w-6 h-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}