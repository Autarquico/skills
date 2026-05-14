import { Config } from "@remotion/cli/config";

// GL backend for Three.js — angle uses hardware GPU; needed for @remotion/three.
// Without this, headless Chromium fails to create a WebGL context.
Config.setChromiumOpenGlRenderer("angle");

// Optional: bump concurrency for faster renders (set to "auto" or a number).
// Config.setConcurrency(8);

// Image format for stills
Config.setVideoImageFormat("jpeg");
