"use client";

import { useEffect, useState } from "react";
import {
  createTwistPayoff,
  createTwistPlant,
  getTwist,
  listTwistPlants,
  transitionTwist,
  updateTwist,
} from "@/lib/api/twists";
import type { Chapter, TwistPayoff, TwistPlan, TwistPlant } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface TwistDetailDrawerProps {
  projectId: string;
  twistId: string | null;
  chapters: Chapter[];
  onClose: () => void;
  onUpdated: () => void;
}

export function TwistDetailDrawer({
  projectId,
  twistId,
  chapters,
  onClose,
  onUpdated,
}: TwistDetailDrawerProps) {
  const t = useTranslations();
  const [twist, setTwist] = useState<TwistPlan | null>(null);
  const [plants, setPlants] = useState<TwistPlant[]>([]);
  const [payoff, setPayoff] = useState<TwistPayoff | null>(null);
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState("");
  const [secretTruth, setSecretTruth] = useState("");
  const [plantSnippet, setPlantSnippet] = useState("");
  const [plantChapterId, setPlantChapterId] = useState("");
  const [payoffChapterId, setPayoffChapterId] = useState("");
  const [minPlants, setMinPlants] = useState(2);

  useEffect(() => {
    if (!twistId) {
      setTwist(null);
      return;
    }
    setLoading(true);
    void Promise.all([getTwist(projectId, twistId), listTwistPlants(projectId, twistId)])
      .then(async ([twistData, plantsData]) => {
        setTwist(twistData);
        setTitle(twistData.title);
        setSecretTruth(twistData.secret_truth ?? "");
        setPlants(plantsData.items);
        if (twistData.payoff) {
          try {
            const { getTwistPayoff } = await import("@/lib/api/twists");
            const payoffData = await getTwistPayoff(projectId, twistId);
            setPayoff(payoffData);
          } catch {
            setPayoff(null);
          }
        } else {
          setPayoff(null);
        }
      })
      .finally(() => setLoading(false));
  }, [projectId, twistId]);

  if (!twistId) return null;

  const handleSave = async () => {
    if (!twist) return;
    await updateTwist(projectId, twist.id, { title, secret_truth: secretTruth });
    onUpdated();
  };

  const handleAddPlant = async () => {
    if (!twistId || !plantChapterId || !plantSnippet.trim()) return;
    await createTwistPlant(projectId, twistId, {
      chapter_id: plantChapterId,
      snippet: plantSnippet.trim(),
      salience: "soft",
    });
    setPlantSnippet("");
    onUpdated();
    const [plantsData, updatedTwist] = await Promise.all([
      listTwistPlants(projectId, twistId),
      getTwist(projectId, twistId),
    ]);
    setPlants(plantsData.items);
    setTwist(updatedTwist);
  };

  const handleRegisterPayoff = async () => {
    if (!twist || !payoffChapterId) return;
    const created = await createTwistPayoff(projectId, twist.id, {
      target_chapter_id: payoffChapterId,
      min_plants: minPlants,
    });
    setPayoff(created);
    onUpdated();
    const updatedTwist = await getTwist(projectId, twist.id);
    setTwist(updatedTwist);
  };

  const handleAbandon = async () => {
    if (!twist) return;
    await transitionTwist(projectId, twist.id, { status: "abandoned" });
    onUpdated();
    onClose();
  };

  return (
    <div className="fixed inset-y-0 right-0 z-40 flex w-full max-w-md flex-col border-l border-slate-200 bg-white shadow-xl">
      <header className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-900">{t("twist.detailTitle")}</h2>
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg px-2 py-1 text-sm text-slate-500 hover:bg-slate-100"
        >
          {t("common.close")}
        </button>
      </header>
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? <p className="text-sm text-slate-500">{t("common.loading")}</p> : null}
        {twist && !loading ? (
          <div className="space-y-6">
            <section className="space-y-3">
              <label className="block text-sm">
                <span className="font-medium text-slate-700">{t("twist.fieldTitle")}</span>
                <input
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium text-slate-700">
                  {t("twist.fieldSecretTruth")}
                  <span className="ml-2 rounded bg-amber-50 px-1.5 py-0.5 text-[10px] uppercase text-amber-700">
                    {t("twist.authorOnlyBadge")}
                  </span>
                </span>
                <textarea
                  value={secretTruth}
                  onChange={(event) => setSecretTruth(event.target.value)}
                  rows={4}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                />
              </label>
              <button
                type="button"
                onClick={() => void handleSave()}
                className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white"
              >
                {t("twist.saveChanges")}
              </button>
            </section>

            <section>
              <h3 className="text-sm font-semibold text-slate-800">
                {t("twist.plantsSection", { count: plants.length })}
              </h3>
              <ul className="mt-2 space-y-2">
                {plants.map((plant) => (
                  <li key={plant.id} className="rounded-lg bg-slate-50 p-2 text-xs text-slate-700">
                    {t("psych.timeline.chapterShort", {
                      number: plant.chapter_number ?? "?",
                    })}
                    :{" "}
                    {plant.snippet}
                  </li>
                ))}
              </ul>
              {twist.status !== "paid_off" ? (
                <div className="mt-3 space-y-2">
                  <select
                    value={plantChapterId}
                    onChange={(event) => setPlantChapterId(event.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                    aria-label={t("twist.selectChapter")}
                  >
                    <option value="">{t("twist.selectChapter")}</option>
                    {chapters.map((chapter) => (
                      <option key={chapter.id} value={chapter.id}>
                        {t("twist.outlineChapterLine", {
                          number: chapter.number,
                          title: chapter.title,
                        })}
                      </option>
                    ))}
                  </select>
                  <textarea
                    value={plantSnippet}
                    onChange={(event) => setPlantSnippet(event.target.value)}
                    placeholder={t("twist.plantSnippetPlaceholder")}
                    rows={2}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  />
                  <button
                    type="button"
                    onClick={() => void handleAddPlant()}
                    className="rounded-lg border border-emerald-300 px-3 py-2 text-sm text-emerald-800 hover:bg-emerald-50"
                  >
                    {t("twist.addPlant")}
                  </button>
                </div>
              ) : null}
            </section>

            <section>
              <h3 className="text-sm font-semibold text-slate-800">{t("twist.payoffSection")}</h3>
              {payoff ? (
                <p className="mt-1 text-xs text-slate-600">
                  {t("twist.payoffSummary", {
                    chapter: payoff.target_chapter_number,
                    minPlants: payoff.min_plants,
                  })}
                </p>
              ) : twist.status !== "paid_off" && twist.status !== "abandoned" ? (
                <div className="mt-2 space-y-2">
                  <select
                    value={payoffChapterId}
                    onChange={(event) => setPayoffChapterId(event.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                    aria-label={t("twist.selectPayoffChapter")}
                  >
                    <option value="">{t("twist.selectPayoffChapter")}</option>
                    {chapters.map((chapter) => (
                      <option key={chapter.id} value={chapter.id}>
                        {t("twist.outlineChapterLine", {
                          number: chapter.number,
                          title: chapter.title,
                        })}
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min={0}
                    value={minPlants}
                    onChange={(event) => setMinPlants(Number(event.target.value))}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                    aria-label={t("twist.minPlantsAria")}
                  />
                  <button
                    type="button"
                    onClick={() => void handleRegisterPayoff()}
                    className="rounded-lg border border-indigo-300 px-3 py-2 text-sm text-indigo-800 hover:bg-indigo-50"
                  >
                    {t("twist.registerPayoff")}
                  </button>
                </div>
              ) : (
                <p className="mt-1 text-xs text-slate-500">{t("twist.noPayoff")}</p>
              )}
            </section>

            {twist.status !== "paid_off" && twist.status !== "abandoned" ? (
              <button
                type="button"
                onClick={() => void handleAbandon()}
                className="text-sm text-red-600 underline"
              >
                {t("twist.abandon")}
              </button>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}
