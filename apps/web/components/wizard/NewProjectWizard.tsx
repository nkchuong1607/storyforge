"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { ApiError } from "@/lib/api/client";
import { createProject } from "@/lib/api/projects";
import type { GenreProfile, ProjectCreateRequest, ProjectTemplate } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { BasicsStep, validateBasics, type BasicsFormData } from "./BasicsStep";
import { ConfirmStep } from "./ConfirmStep";
import { GenreStep } from "./GenreStep";
import { TemplateStep } from "./TemplateStep";
import { WizardLayout } from "./WizardLayout";

const TOTAL_STEPS = 4;

export function NewProjectWizard() {
  const t = useTranslations();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [basics, setBasics] = useState<BasicsFormData>({
    title: "",
    description: "",
    language: "vi",
  });
  const [genre, setGenre] = useState<GenreProfile | null>(null);
  const [template, setTemplate] = useState<ProjectTemplate | null>(null);
  const [basicsErrors, setBasicsErrors] = useState<Partial<Record<keyof BasicsFormData, string>>>(
    {},
  );
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const createRequest: ProjectCreateRequest | null = useMemo(() => {
    if (!genre || !template) return null;
    return {
      title: basics.title.trim(),
      description: basics.description.trim() || undefined,
      language: basics.language,
      genre_profile: genre,
      template,
    };
  }, [basics, genre, template]);

  const stepTitles = [
    t("wizard.stepBasics"),
    t("wizard.stepGenreSelect"),
    t("wizard.stepTemplateSelect"),
    t("wizard.stepConfirm"),
  ];
  const stepTitle = stepTitles[step - 1];

  const handleNext = () => {
    if (step === 1) {
      const errors = validateBasics(basics, t);
      setBasicsErrors(errors);
      if (Object.keys(errors).length > 0) return;
    }
    if (step === 2 && !genre) return;
    if (step === 3 && !template) return;
    if (step < TOTAL_STEPS) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    if (!createRequest || isSubmitting) return;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const project = await createProject(createRequest);
      router.push(`/projects/${project.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.code === "slug_conflict") {
        const suggested = err.details?.[0]?.suggested_slug as string | undefined;
        setSubmitError(
          suggested
            ? t("wizard.slugConflictSuggested", { suggested })
            : t("wizard.slugConflict"),
        );
      } else {
        setSubmitError(t("wizard.errorCreate"));
      }
      setIsSubmitting(false);
    }
  };

  const nextDisabled =
    (step === 2 && !genre) ||
    (step === 3 && !template) ||
    (step === 4 && isSubmitting) ||
    (step === 1 && Object.keys(basicsErrors).length > 0);

  return (
    <AppShell>
      <WizardLayout
        currentStep={step}
        totalSteps={TOTAL_STEPS}
        stepTitle={stepTitle}
        onBack={step > 1 ? handleBack : undefined}
        onNext={step < TOTAL_STEPS ? handleNext : handleSubmit}
        nextLabel={step === TOTAL_STEPS ? t("wizard.create") : t("wizard.nextExtended")}
        nextDisabled={nextDisabled}
        showBack={step > 1}
      >
        {step === 1 ? (
          <BasicsStep data={basics} onChange={setBasics} errors={basicsErrors} />
        ) : null}
        {step === 2 ? <GenreStep selected={genre} onSelect={setGenre} /> : null}
        {step === 3 ? <TemplateStep selected={template} onSelect={setTemplate} /> : null}
        {step === 4 && createRequest ? (
          <ConfirmStep data={createRequest} error={submitError} isSubmitting={isSubmitting} />
        ) : null}
      </WizardLayout>
    </AppShell>
  );
}
