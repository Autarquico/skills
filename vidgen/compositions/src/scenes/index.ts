/**
 * Scene library registry — Day 3 expanded.
 *
 * The render-director consults this to map `script.json` scene `type` strings
 * to React components. Add new scenes here to make them callable from scripts.
 */

import { TextCard, TextCardSchema, type TextCardProps } from "./TextCard";
import { HeroTitle, HeroTitleSchema, type HeroTitleProps } from "./HeroTitle";
import { ListItem, ListItemSchema, type ListItemProps } from "./ListItem";
import { DialogueBeat, DialogueBeatSchema, type DialogueBeatProps } from "./DialogueBeat";
import { MasterQuote, MasterQuoteSchema, type MasterQuoteProps } from "./MasterQuote";
import { MarkReveal, MarkRevealSchema, type MarkRevealProps } from "./MarkReveal";
import { ClosingCard, ClosingCardSchema, type ClosingCardProps } from "./ClosingCard";
import { StatReveal, StatRevealSchema, type StatRevealProps } from "./StatReveal";
import { KineticType, KineticTypeSchema, type KineticTypeProps } from "./KineticType";
import { ThreeScene, ThreeSceneSchema, type ThreeSceneProps } from "./ThreeScene";
import { LottiePlay, LottiePlaySchema, type LottiePlayProps } from "./LottiePlay";
import { KpiRow, KpiRowSchema, type KpiRowProps } from "./KpiRow";
import { UIMockMobile, UIMockMobileSchema, type UIMockMobileProps } from "./UIMockMobile";
import { UIMockDesktop, UIMockDesktopSchema, type UIMockDesktopProps } from "./UIMockDesktop";
import { ChatOverlay, ChatOverlaySchema, type ChatOverlayProps } from "./ChatOverlay";

// Stage 1 expansion (photo-led / testimonial / oferta / tutorial / antes-después)
import { PhotoCard, PhotoCardSchema, type PhotoCardProps } from "./PhotoCard";
import { PhotoBackground, PhotoBackgroundSchema, type PhotoBackgroundProps } from "./PhotoBackground";
import { PhotoSlideshow, PhotoSlideshowSchema, type PhotoSlideshowProps } from "./PhotoSlideshow";
import { QuoteCard, QuoteCardSchema, type QuoteCardProps } from "./QuoteCard";
import { PriceCard, PriceCardSchema, type PriceCardProps } from "./PriceCard";
import { StepCard, StepCardSchema, type StepCardProps } from "./StepCard";
import { SplitScreen, SplitScreenSchema, type SplitScreenProps } from "./SplitScreen";
import { ScreenAnnotation, ScreenAnnotationSchema, type ScreenAnnotationProps } from "./ScreenAnnotation";

// Stage 2 expansion (newsletter / podcast / data viz / lyric)
import { PhotoCardGrid, PhotoCardGridSchema, type PhotoCardGridProps } from "./PhotoCardGrid";
import { WaveformOverlay, WaveformOverlaySchema, type WaveformOverlayProps } from "./WaveformOverlay";
import { BarChart, BarChartSchema, type BarChartProps } from "./BarChart";
import { LineChart, LineChartSchema, type LineChartProps } from "./LineChart";
import { LyricLine, LyricLineSchema, type LyricLineProps } from "./LyricLine";

// Stage 3 — local AI video generation (LTX-Video)
import { LocalVideoClip, LocalVideoClipSchema, type LocalVideoClipProps } from "./LocalVideoClip";

export const SCENES = {
  // Editorial typography
  "text-card": { component: TextCard, schema: TextCardSchema },
  "hero-title": { component: HeroTitle, schema: HeroTitleSchema },
  "list-item": { component: ListItem, schema: ListItemSchema },
  "dialogue-beat": { component: DialogueBeat, schema: DialogueBeatSchema },
  "master-quote": { component: MasterQuote, schema: MasterQuoteSchema },
  "mark-reveal": { component: MarkReveal, schema: MarkRevealSchema },
  "closing-card": { component: ClosingCard, schema: ClosingCardSchema },
  "stat-reveal": { component: StatReveal, schema: StatRevealSchema },
  "kpi-row": { component: KpiRow, schema: KpiRowSchema },

  // Motion expanded (Day 3)
  "kinetic-type": { component: KineticType, schema: KineticTypeSchema },
  "three-scene": { component: ThreeScene, schema: ThreeSceneSchema },
  "lottie-play": { component: LottiePlay, schema: LottiePlaySchema },

  // UI mocks (Day 3, refactored from session components)
  "ui-mock-mobile": { component: UIMockMobile, schema: UIMockMobileSchema },
  "ui-mock-desktop": { component: UIMockDesktop, schema: UIMockDesktopSchema },
  "chat-overlay": { component: ChatOverlay, schema: ChatOverlaySchema },

  // Stage 1 expansion — photo-led / testimonial / oferta / tutorial / antes-después
  "photo-card": { component: PhotoCard, schema: PhotoCardSchema },
  "photo-background": { component: PhotoBackground, schema: PhotoBackgroundSchema },
  "photo-slideshow": { component: PhotoSlideshow, schema: PhotoSlideshowSchema },
  "quote-card": { component: QuoteCard, schema: QuoteCardSchema },
  "price-card": { component: PriceCard, schema: PriceCardSchema },
  "step-card": { component: StepCard, schema: StepCardSchema },
  "split-screen": { component: SplitScreen, schema: SplitScreenSchema },
  "screen-annotation": { component: ScreenAnnotation, schema: ScreenAnnotationSchema },

  // Stage 2 — newsletter / podcast / data viz / lyric
  "photo-card-grid": { component: PhotoCardGrid, schema: PhotoCardGridSchema },
  "waveform-overlay": { component: WaveformOverlay, schema: WaveformOverlaySchema },
  "bar-chart": { component: BarChart, schema: BarChartSchema },
  "line-chart": { component: LineChart, schema: LineChartSchema },
  "lyric-line": { component: LyricLine, schema: LyricLineSchema },

  // Stage 3 — local AI video generation
  "local-video-clip": { component: LocalVideoClip, schema: LocalVideoClipSchema },
} as const;

export type SceneType = keyof typeof SCENES;

export function getScene(type: string) {
  if (type in SCENES) return SCENES[type as SceneType];
  return null;
}

export function listScenes(): string[] {
  return Object.keys(SCENES);
}

// Re-export types for downstream consumers
export type {
  TextCardProps,
  HeroTitleProps,
  ListItemProps,
  DialogueBeatProps,
  MasterQuoteProps,
  MarkRevealProps,
  ClosingCardProps,
  StatRevealProps,
  KineticTypeProps,
  ThreeSceneProps,
  LottiePlayProps,
  KpiRowProps,
  UIMockMobileProps,
  UIMockDesktopProps,
  ChatOverlayProps,
};
