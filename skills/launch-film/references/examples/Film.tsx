import React from "react";
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { SCENES } from "./timeline";
import { SceneLogo } from "./scenes/A_Logo";
import { SceneIdea } from "./scenes/B_Idea";
import { SceneChoose } from "./scenes/C_Choose";
import { SceneCreative } from "./scenes/D_Creative";
import { SceneSpaces } from "./scenes/E_Spaces";
import { SceneBringPhoto } from "./scenes/F_BringPhoto";
import { SceneExplore } from "./scenes/G_Explore";
import { SceneCake } from "./scenes/HIJ_Cake";
import { SceneCup } from "./scenes/KL_Cup";
import { SceneProduct } from "./scenes/M_Product";
import { SceneFinale } from "./scenes/NO_Finale";
import { SoundTrack } from "./SoundTrack";
import { Grain } from "./components/Media";
import { C } from "./theme";

export const Film: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <Sequence name="A · Meet Sloosh" from={SCENES.logo.from} durationInFrames={SCENES.logo.dur} premountFor={fps}>
        <SceneLogo />
      </Sequence>
      <Sequence name="B · You bring the idea" from={SCENES.idea.from} durationInFrames={SCENES.idea.dur} premountFor={fps}>
        <SceneIdea />
      </Sequence>
      <Sequence name="C · Choose what you want to make" from={SCENES.choose.from} durationInFrames={SCENES.choose.dur} premountFor={fps}>
        <SceneChoose />
      </Sequence>
      <Sequence name="D · Creative workflows" from={SCENES.creative.from} durationInFrames={SCENES.creative.dur} premountFor={fps}>
        <SceneCreative />
      </Sequence>
      <Sequence name="E · Prepared to help you get there" from={SCENES.spaces.from} durationInFrames={SCENES.spaces.dur} premountFor={fps}>
        <SceneSpaces />
      </Sequence>
      <Sequence name="F · Bring your photo" from={SCENES.bringPhoto.from} durationInFrames={SCENES.bringPhoto.dur} premountFor={fps}>
        <SceneBringPhoto />
      </Sequence>
      <Sequence name="G · Explore the possibilities" from={SCENES.explore.from} durationInFrames={SCENES.explore.dur} premountFor={fps}>
        <SceneExplore />
      </Sequence>
      <Sequence name="H–J · Details / Your cake / On the moon" from={SCENES.cake.from} durationInFrames={SCENES.cake.dur} premountFor={fps}>
        <SceneCake />
      </Sequence>
      <Sequence name="K–L · Your photograph / A new visual story" from={SCENES.cup.from} durationInFrames={SCENES.cup.dur} premountFor={fps}>
        <SceneCup />
      </Sequence>
      <Sequence name="M · Your product" from={SCENES.product.from} durationInFrames={SCENES.product.dur} premountFor={fps}>
        <SceneProduct />
      </Sequence>
      <Sequence name="N–O · A campaign that feels like you + resolve" from={SCENES.finale.from} durationInFrames={SCENES.finale.dur} premountFor={fps}>
        <SceneFinale />
      </Sequence>
      <Grain opacity={0.07} />
      <SoundTrack />
    </AbsoluteFill>
  );
};
