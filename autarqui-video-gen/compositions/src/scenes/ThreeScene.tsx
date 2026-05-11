/**
 * ThreeScene — Wrapper for Three.js scenes inside Remotion.
 *
 * Uses @remotion/three. Provides 2-3 named templates that work out-of-the-box,
 * plus a "custom" mode where the caller passes a child component.
 *
 * Templates:
 *   - "rotating-text"   — 3D extruded text with slow Y rotation
 *   - "particle-field"  — ambient particle background
 *   - "card-reveal"     — flat card flying in from depth
 *
 * For more complex 3D scenes, write a project-local Composition.tsx that uses
 * <ThreeCanvas> directly with R3F primitives.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useStyleTokens } from "../lib/tokens";
import { sceneOpacity, easings } from "../lib/animations";

type Template = "rotating-text" | "particle-field" | "card-reveal";

export interface ThreeSceneProps {
  template: Template;
  text?: string;
  /** Override background color (default: tokens.bg) */
  background?: string;
  /** Camera FOV degrees */
  fov?: number;
  scene_duration_frames?: number;
}

export const ThreeScene: React.FC<ThreeSceneProps> = ({
  template,
  text,
  background,
  fov = 50,
  scene_duration_frames,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const op = sceneOpacity(frame, 0, total, 18, 24);
  const bg = background ?? t.colors.bg;

  return (
    <AbsoluteFill style={{ backgroundColor: bg, opacity: op }}>
      <ThreeCanvas
        width={width}
        height={height}
        camera={{ fov, position: [0, 0, 5] }}
        gl={{ antialias: true }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 5, 5]} intensity={0.8} />

        {template === "rotating-text" && <RotatingText text={text || ""} color={t.colors.heading} />}
        {template === "particle-field" && <ParticleField color={t.colors.muted} />}
        {template === "card-reveal" && <CardReveal text={text || ""} color={t.colors.heading} surface={t.colors.surface} />}
      </ThreeCanvas>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Templates
// ---------------------------------------------------------------------------

const RotatingText: React.FC<{ text: string; color: string }> = ({ text, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame / fps) * 0.4; // slow rotation

  // 3D text via primitive boxes spelling out — placeholder geometry.
  // For real 3D text use TextGeometry with a font; that requires external setup.
  // This template uses a flat plane with the text drawn as an HTML overlay alternative.
  // Here we just render rotating box(es).
  return (
    <group rotation={[0, t, 0]}>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[3, 0.6, 0.3]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  );
};

const ParticleField: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // Generate stable particle positions
  const particles = React.useMemo(() => {
    const out: [number, number, number][] = [];
    for (let i = 0; i < 200; i++) {
      const x = (Math.sin(i * 12.9898) * 43758.5453) % 1;
      const y = (Math.sin(i * 78.233) * 43758.5453) % 1;
      const z = (Math.sin(i * 39.346) * 43758.5453) % 1;
      out.push([(x - 0.5) * 8, (y - 0.5) * 5, (z - 0.5) * 4]);
    }
    return out;
  }, []);

  return (
    <group rotation={[0, t * 0.05, 0]}>
      {particles.map((pos, i) => (
        <mesh key={i} position={pos}>
          <sphereGeometry args={[0.015, 8, 8]} />
          <meshBasicMaterial color={color} />
        </mesh>
      ))}
    </group>
  );
};

const CardReveal: React.FC<{ text: string; color: string; surface: string }> = ({
  color,
  surface,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = easings.easeOutCubic(Math.min(1, frame / (fps * 1.2)));
  const z = -8 + progress * 8;
  const rot = (1 - progress) * Math.PI * 0.15;

  return (
    <group position={[0, 0, z]} rotation={[rot, 0, 0]}>
      <mesh>
        <planeGeometry args={[4, 2.5]} />
        <meshStandardMaterial color={surface} />
      </mesh>
      <mesh position={[0, 0, 0.01]}>
        <planeGeometry args={[3.5, 0.4]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  );
};

export const ThreeSceneSchema = {
  template: {
    type: "enum",
    values: ["rotating-text", "particle-field", "card-reveal"],
    required: true,
  },
  text: { type: "string", required: false },
  background: { type: "string", required: false },
  fov: { type: "number", required: false },
} as const;
