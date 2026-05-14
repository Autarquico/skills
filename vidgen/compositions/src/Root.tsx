/**
 * Root.tsx — Composition registry.
 *
 * Each project's `projects/<id>/Composition.tsx` exports:
 *   - default: React.FC (the composition)
 *   - meta: { id, durationInFrames, fps, width, height, defaultProps? }
 *
 * To register a new project, add an import + entry to `PROJECTS` below.
 * The render-director adds the import automatically when generating a project.
 */

import * as React from "react";
import { Composition } from "remotion";

// === REGISTERED PROJECTS ====================================================
// (Generated/maintained by render-director — list grows as videos are produced.)

import * as DeltaLaunchDemo from "./projects/delta-launch-demo/Composition";
import * as DeltaVision60s from "./projects/delta-vision-60s/Composition";
import * as ValidationTest from "./projects/validation-test/Composition";
import * as DemoFotoInstagram from "./projects/demo-foto-instagram/Composition";
import * as DemoTestimonial from "./projects/demo-testimonial/Composition";
import * as DemoAnuncioOferta from "./projects/demo-anuncio-oferta/Composition";
import * as DemoTutorial60s from "./projects/demo-tutorial-60s/Composition";
import * as DemoAntesDespues from "./projects/demo-antes-despues/Composition";
import * as DemoNewsletter from "./projects/demo-newsletter/Composition";
import * as DemoPodcastResumen from "./projects/demo-podcast-resumen/Composition";
import * as DemoDataViz from "./projects/demo-data-viz/Composition";
import * as DemoLyric from "./projects/demo-lyric/Composition";
import * as DemoHowItWorks from "./projects/demo-how-it-works/Composition";
import * as DemoLocalVideo from "./projects/demo-local-video/Composition";

const PROJECTS = [DeltaLaunchDemo, DeltaVision60s, ValidationTest, DemoFotoInstagram, DemoTestimonial, DemoAnuncioOferta, DemoTutorial60s, DemoAntesDespues, DemoNewsletter, DemoPodcastResumen, DemoDataViz, DemoLyric, DemoHowItWorks, DemoLocalVideo];

// ============================================================================

export const Root: React.FC = () => {
  return (
    <>
      {PROJECTS.map((mod: any) => (
        <Composition
          key={mod.meta.id}
          id={mod.meta.id}
          component={mod.default}
          durationInFrames={mod.meta.durationInFrames}
          fps={mod.meta.fps}
          width={mod.meta.width}
          height={mod.meta.height}
          defaultProps={mod.meta.defaultProps || {}}
        />
      ))}
    </>
  );
};
