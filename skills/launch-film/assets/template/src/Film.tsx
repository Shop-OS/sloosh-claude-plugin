import React from "react";
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { SCENES, VO } from "./timeline";
import { Grain } from "./components/Media";
import { SoundTrack, speechFrom } from "./SoundTrack";
import { CUES } from "./cues";
import { C } from "./theme";
import { PunctuationWord } from "./recipes/PunctuationWord";

// One <Sequence> per scene; scenes are their own files in src/scenes/.
export const Film: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <Sequence name="Open" from={SCENES.open.from} durationInFrames={SCENES.open.dur} premountFor={fps}>
        <PunctuationWord text="HELLO." bg={C.accent} color={C.ink} />
      </Sequence>
      <Sequence name="Next" from={SCENES.next.from} durationInFrames={SCENES.next.dur} premountFor={fps}>
        <PunctuationWord text="WORLD." bg={C.ink} color={C.white} />
      </Sequence>
      <Grain opacity={0.07} />
      <SoundTrack vo={[]} cues={CUES} speech={speechFrom(VO)} />
    </AbsoluteFill>
  );
};
