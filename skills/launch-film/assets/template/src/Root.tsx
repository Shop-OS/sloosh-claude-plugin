import { Composition } from "remotion";
import { Film } from "./Film";
import { FPS, TOTAL_FRAMES } from "./timeline";

// Register one <Composition> per part of a multi-part film, plus a FullFilm.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Film" component={Film} durationInFrames={TOTAL_FRAMES} fps={FPS} width={1920} height={1080} />
    </>
  );
};
