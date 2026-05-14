/**
 * animations.ts — Reusable easing and motion helpers tied to style tokens.
 */

import type { StyleTokens } from "./tokens";

// ============================================================================
// EASINGS
// ============================================================================

export const easings = {
  linear: (t: number) => t,
  easeOutCubic: (t: number) => 1 - Math.pow(1 - t, 3),
  easeInCubic: (t: number) => t * t * t,
  easeInOutCubic: (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  easeOutQuart: (t: number) => 1 - Math.pow(1 - t, 4),
  easeOutExpo: (t: number) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
};

export function easingByName(name: string): (t: number) => number {
  switch (name) {
    case "linear":
      return easings.linear;
    case "ease-in-cubic":
      return easings.easeInCubic;
    case "ease-out-cubic":
      return easings.easeOutCubic;
    case "ease-in-out-cubic":
      return easings.easeInOutCubic;
    case "ease-out-quart":
      return easings.easeOutQuart;
    case "ease-out-expo":
      return easings.easeOutExpo;
    default:
      return easings.easeOutCubic;
  }
}

// ============================================================================
// FADE / SCENE OPACITY HELPERS
// ============================================================================

export interface FadeOptions {
  fps?: number;
}

/**
 * Linear/eased fade-in across [inFrame, inFrame + durationFrames]. Returns 0..1.
 */
export function fadeIn(
  frame: number,
  inFrame: number,
  durationFrames: number,
  ease: (t: number) => number = easings.easeOutCubic,
): number {
  const t = (frame - inFrame) / durationFrames;
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  return ease(t);
}

/**
 * Symmetric fade-in then fade-out over a window [start, end].
 */
export function sceneOpacity(
  frame: number,
  start: number,
  end: number,
  fadeInFrames: number,
  fadeOutFrames: number,
  ease: (t: number) => number = easings.easeOutCubic,
): number {
  if (frame < start || frame > end) return 0;
  const inOp = Math.min(1, (frame - start) / fadeInFrames);
  const outOp = Math.min(1, (end - frame) / fadeOutFrames);
  return ease(Math.min(inOp, outOp));
}

// ============================================================================
// MOTION TYPE → CSS TRANSFORM (for non-fade motion types)
// ============================================================================

/**
 * Returns a CSS transform string for a motion type at progress t (0..1).
 * Use for `style.motion.in.type` other than "fade".
 */
export function motionTransform(type: string, progress: number): string {
  const p = Math.max(0, Math.min(1, progress));
  switch (type) {
    case "slide-up":
      return `translateY(${(1 - p) * 30}px)`;
    case "slide-down":
      return `translateY(${(1 - p) * -30}px)`;
    case "slide-left":
      return `translateX(${(1 - p) * 30}px)`;
    case "slide-right":
      return `translateX(${(1 - p) * -30}px)`;
    case "scale-up":
      return `scale(${0.92 + p * 0.08})`;
    case "scale-down":
      return `scale(${1.08 - p * 0.08})`;
    case "fade":
    case "cut":
    default:
      return "none";
  }
}

// ============================================================================
// PACING → DEFAULT DURATIONS
// ============================================================================

/**
 * Convert pacing keyword + style tokens into default in/out durations in frames.
 * Used by scenes that don't override timing explicitly.
 */
export function defaultPacing(tokens: StyleTokens, fps: number) {
  const pacingMultiplier = { slow: 1.0, medium: 0.65, fast: 0.4 }[tokens.motion.pacing] || 1.0;
  const inMs = tokens.motion.in.duration_ms * pacingMultiplier;
  const outMs = tokens.motion.out.duration_ms * pacingMultiplier;
  return {
    inFrames: Math.round((inMs / 1000) * fps),
    outFrames: Math.round((outMs / 1000) * fps),
  };
}
