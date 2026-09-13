declare module "jest-axe" {
  import type { AxeResults } from "axe-core";

  export function axe(container: Element | Document): Promise<AxeResults>;

  export function toHaveNoViolations(results: AxeResults): {
    pass: boolean;
    message: () => string;
  };
}
