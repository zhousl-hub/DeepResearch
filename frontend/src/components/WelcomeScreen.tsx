import { InputForm } from "./InputForm";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string,
    model: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
}) => (
  <div className="h-full flex flex-col items-center justify-center text-center px-6 flex-1 w-full max-w-3xl mx-auto gap-5">
    <div className="space-y-3">
      <h1 className="text-3xl md:text-4xl font-semibold text-neutral-100 leading-tight">
        欢迎你！专业、广博、迅捷的行业专家！
      </h1>
      <p className="text-base md:text-lg text-neutral-400">
        请在下方写入你的要求，让我们为你提供专业的帮助
      </p>
    </div>
    <div className="w-full mt-4">
      <InputForm
        onSubmit={handleSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        hasHistory={false}
      />
    </div>
    <p className="text-xs text-neutral-500">
      基于LLM的深度搜索
    </p>
  </div>
);
