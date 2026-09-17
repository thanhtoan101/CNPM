import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";
import { createDemoState, isDemoState, STORAGE_KEY } from "./domain";
import type { DemoState } from "./domain";

type Store = { state: DemoState; update: (action: (state: DemoState) => DemoState) => boolean; error: string };
const Context = createContext<Store | null>(null);

function restore(): { state: DemoState; error: string } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { state: createDemoState(), error: "" };
    const state = JSON.parse(raw);
    if (!isDemoState(state)) throw new Error("Invalid saved demo data");
    return { state, error: "" };
  } catch {
    return { state: createDemoState(), error: "Saved demo data could not be read. Sample data is shown; the next successful change will replace the saved snapshot." };
  }
}

export function DemoProvider({ children }: { children: ReactNode }) {
  const [saved, setSaved] = useState(restore);
  const update = (action: (state: DemoState) => DemoState) => {
    try {
      const next = action(saved.state);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      setSaved({ state: next, error: "" });
      return true;
    } catch (error) {
      setSaved(current => ({ ...current, error: error instanceof Error ? error.message : "Changes could not be saved. Check browser storage and retry." }));
      return false;
    }
  };
  return <Context.Provider value={{ state: saved.state, update, error: saved.error }}>{children}</Context.Provider>;
}
export function useDemo() {
  const store = useContext(Context);
  if (!store) throw new Error("DemoProvider is required");
  return store;
}
