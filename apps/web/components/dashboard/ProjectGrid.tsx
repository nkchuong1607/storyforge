import type { ProjectSummary } from "@/lib/api/types";
import { ProjectCard } from "./ProjectCard";

interface ProjectGridProps {
  projects: ProjectSummary[];
}

export function ProjectGrid({ projects }: ProjectGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
}
