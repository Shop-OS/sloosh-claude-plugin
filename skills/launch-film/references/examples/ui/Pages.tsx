import React from "react";
import { C, FONT } from "../theme";
import { IMG, ImgAsset } from "../assets";
import { Photo } from "../components/Media";
import { clamp01, E, prog } from "../lib/anim";
import {
  Accent,
  EyeBadge,
  Heading,
  ModelCard,
  NavBar,
  OutlineBtn,
  SeeAll,
  ToolCard,
  UploadSlot,
  WorkflowCard,
  YellowBtn,
} from "./Kit";
import { IChevronDown, IHeart, IImage, IPlay, IPlus, ISearch, IShare, ISliders, IVideo, ILock } from "./Icons";

export const PAGE_W = 1440;
const PAD = 26;
const INNER = PAGE_W - PAD * 2;

// ===================================================================== EXPLORE

export const EXPLORE_LAYOUT = {
  hero: { y: 64, h: 600 },
  models: { y: 712 },
  templates: { y: 960 },
  tools: { y: 1690 },
  spacelab: { y: 2030 },
  height: 2560,
};

export type ExploreState = {
  /** 0..1 per tool card highlight */
  toolHighlight?: number[];
  toolLift?: number[];
  heroProgress?: number;
};

const MODELS: { label: string; img: ImgAsset; dot: string; crop?: { x: number; y: number; w: number; h: number } }[] = [
  { label: "Seedance 2.5", img: IMG.digital, dot: "#3B82F6" },
  { label: "MiniMax H3 Max", img: IMG.studio, dot: "#F43F5E" },
  { label: "Kling V3 Omni", img: IMG.landscape, dot: "#10B981" },
  { label: "Nano Banana Pro", img: IMG.eye, dot: "#FBBF24" },
  { label: "GPT-image-2", img: IMG.print, dot: "#111111" },
  { label: "Seedream 5 Pro", img: IMG.cave, dot: "#6366F1" },
];

export const TOOLS: { label: string; img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } }[] = [
  { label: "Food Styling", img: IMG.cakeSrc, crop: { x: 930, y: 480, w: 420, h: 420 } },
  { label: "Fashion Campaign", img: IMG.mFashion },
  { label: "On-Model Shoot", img: IMG.mOnModel },
  { label: "Sketch to Render", img: IMG.print, crop: { x: 1180, y: 300, w: 420, h: 420 } },
  { label: "Upscale", img: IMG.eye, crop: { x: 500, y: 140, w: 520, h: 520 } },
  { label: "Virtual Try-on", img: IMG.mTryOn },
  { label: "Jewellery Shoot", img: IMG.mJewel },
  { label: "Selfie to Studio", img: IMG.mSelfie },
];

const TEMPLATE_COLS: { img: ImgAsset; h: number; crop?: { x: number; y: number; w: number; h: number } }[][] = [
  [
    { img: IMG.impasto, h: 250 },
    { img: IMG.mGrid, h: 200 },
    { img: IMG.handover, h: 170 },
  ],
  [
    { img: IMG.alt02, h: 380, crop: { x: 480, y: 0, w: 640, h: 940 } },
    { img: IMG.mEditorial, h: 250 },
  ],
  [
    { img: IMG.alt03, h: 380, crop: { x: 560, y: 0, w: 640, h: 941 } },
    { img: IMG.mClay, h: 250 },
  ],
  [
    { img: IMG.commission, h: 200 },
    { img: IMG.mSwap, h: 220 },
    { img: IMG.approval, h: 200 },
  ],
  [
    { img: IMG.photographer, h: 200 },
    { img: IMG.nextCake, h: 200 },
    { img: IMG.mPlace, h: 220 },
  ],
];

export const ExplorePage: React.FC<{ state?: ExploreState; logoLook?: { x: number; y: number } }> = ({ state = {}, logoLook }) => {
  const hl = state.toolHighlight ?? [];
  const lift = state.toolLift ?? [];
  const L = EXPLORE_LAYOUT;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: PAGE_W, height: L.height, background: C.ink, fontFamily: FONT.ui }}>
      <div style={{ position: "absolute", left: 0, top: 0 }}>
        <NavBar width={PAGE_W} active="Explore" logoLook={logoLook} />
      </div>
      {/* hero */}
      <div style={{ position: "absolute", left: 0, top: L.hero.y, width: PAGE_W, height: L.hero.h, overflow: "hidden" }}>
        <Photo img={IMG.alt01} width={PAGE_W} height={L.hero.h} crop={{ x: 0, y: 40, w: 1672, h: 697 }} />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(90deg, rgba(0,0,0,0.72) 0%, rgba(0,0,0,0.25) 46%, rgba(0,0,0,0) 70%)" }} />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(10,10,10,1) 0%, rgba(10,10,10,0) 28%)" }} />
        <div style={{ position: "absolute", left: 46, top: 190 }}>
          <Heading size={68}>
            Put yourself
            <br />
            in <Accent>any video.</Accent>
          </Heading>
          <div style={{ marginTop: 18, width: 470, fontSize: 18, lineHeight: 1.45, color: C.textSubtle }}>
            Pick a video and add your photo. You get it back with you in every shot.
          </div>
          <div style={{ marginTop: 26 }}>
            <YellowBtn label="Clone a video" icon={<IPlay size={17} color={C.ink} />} />
          </div>
        </div>
        <div style={{ position: "absolute", left: 46, right: 46, bottom: 46, display: "flex", gap: 12 }}>
          {[0, 1, 2, 3].map((i) => (
            <div key={i} style={{ flex: 1, height: 3, borderRadius: 2, background: "rgba(255,255,255,0.28)", overflow: "hidden" }}>
              <div style={{ width: i === 0 ? `${(state.heroProgress ?? 0.35) * 100}%` : 0, height: "100%", background: C.yellow }} />
            </div>
          ))}
        </div>
      </div>
      {/* models */}
      <div style={{ position: "absolute", left: PAD, top: L.models.y, width: INNER }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 18 }}>
          <Heading size={26}>Pick the right model for your shot.</Heading>
          <SeeAll />
        </div>
        <div style={{ display: "flex", gap: 16 }}>
          {MODELS.map((m) => (
            <ModelCard key={m.label} img={m.img} label={m.label} dot={m.dot} width={(INNER - 80) / 6} height={160} />
          ))}
        </div>
      </div>
      {/* templates */}
      <div style={{ position: "absolute", left: PAD, top: L.templates.y, width: INNER }}>
        <Heading size={26} style={{ marginBottom: 18 }}>
          Recreate what works for you.
        </Heading>
        <div style={{ display: "flex", gap: 14 }}>
          {TEMPLATE_COLS.map((col, i) => (
            <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", gap: 14 }}>
              {col.map((t, j) => (
                <div key={j} style={{ position: "relative", borderRadius: 12, overflow: "hidden" }}>
                  <Photo img={t.img} crop={t.crop} width={(INNER - 56) / 5} height={t.h} />
                  <div style={{ position: "absolute", left: 10, top: 10 }}>
                    <EyeBadge size={22} />
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
      {/* tools */}
      <div style={{ position: "absolute", left: PAD, top: L.tools.y, width: INNER }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
          <Heading size={26}>Tools you might like.</Heading>
          <div style={{ display: "flex", background: C.layer1, borderRadius: 12, padding: 4, gap: 4, border: `1px solid ${C.line}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, background: C.layer3, borderRadius: 9, padding: "7px 14px", color: C.text, fontSize: 14, fontWeight: 600 }}>
              <IImage size={15} /> Image
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", color: C.textMuted, fontSize: 14, fontWeight: 500 }}>
              <IVideo size={15} /> Video
            </div>
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
          {TOOLS.map((t, i) => (
            <ToolCard key={t.label} img={t.img} crop={t.crop} label={t.label} width={(INNER - 48) / 4} highlight={hl[i] ?? 0} lift={lift[i] ?? 0} />
          ))}
        </div>
      </div>
      {/* spacelab block */}
      <div
        style={{
          position: "absolute",
          left: PAD,
          top: L.spacelab.y,
          width: INNER,
          height: 470,
          borderRadius: 22,
          overflow: "hidden",
          background: C.layer1,
          display: "flex",
        }}
      >
        <div style={{ width: 560, padding: "64px 54px", boxSizing: "border-box", position: "relative" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, color: C.textMuted, fontSize: 15, marginBottom: 22 }}>Spacelab</div>
          <Heading size={52}>
            Build your
            <br />
            own <Accent>workflow.</Accent>
          </Heading>
          <div style={{ marginTop: 22, fontSize: 17, lineHeight: 1.5, color: C.textSubtle, width: 440 }}>
            Chain models into one flow and run it on your own inputs. Save it as a space and reuse it, or share it with your team.
          </div>
          <div style={{ display: "flex", gap: 12, marginTop: 30 }}>
            <OutlineBtn label="Browse spaces" />
            <YellowBtn label="Create a space" icon={<IPlus size={16} color={C.ink} />} />
          </div>
        </div>
        <div style={{ flex: 1, background: C.yellow, position: "relative" }}>
          <div
            style={{
              position: "absolute",
              left: 60,
              top: 56,
              right: 60,
              bottom: 40,
              background: C.ink,
              borderRadius: 26,
              boxShadow: "0 30px 60px rgba(120,90,0,0.45)",
              overflow: "hidden",
            }}
          >
            <MiniGraph />
          </div>
        </div>
      </div>
    </div>
  );
};

/** Small node graph used inside the Spacelab promo card. */
const MiniGraph: React.FC = () => (
  <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(rgba(255,255,255,0.09) 1px, transparent 1px)", backgroundSize: "16px 16px" }}>
    <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
      <path d="M200 120 C 300 120, 300 190, 400 190" stroke="rgba(255,255,255,0.35)" strokeWidth="2" fill="none" />
      <path d="M200 250 C 300 250, 300 200, 400 200" stroke="rgba(255,255,255,0.35)" strokeWidth="2" fill="none" />
    </svg>
    <div style={{ position: "absolute", left: 40, top: 70, width: 160, height: 100, borderRadius: 12, border: "1.5px solid rgba(52,211,153,0.4)", background: "rgba(52,211,153,0.08)", color: C.textSubtle, fontSize: 12, padding: 12, boxSizing: "border-box" }}>
      Place my cake on the moon.
    </div>
    <div style={{ position: "absolute", left: 40, top: 200, borderRadius: 12, overflow: "hidden", border: "1.5px solid rgba(96,165,250,0.5)" }}>
      <Photo img={IMG.cakeSrc} crop={{ x: 900, y: 480, w: 480, h: 360 }} width={160} height={110} />
    </div>
    <div style={{ position: "absolute", left: 400, top: 120, borderRadius: 12, overflow: "hidden", border: "1.5px solid rgba(254,204,21,0.6)" }}>
      <Photo img={IMG.cakeMoon} width={220} height={150} />
    </div>
  </div>
);

// ===================================================================== SPACES

export type SpaceCardDef = {
  title: string;
  blurb: string;
  inputs: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number }; flip?: boolean }[];
  output: { img: ImgAsset; crop?: { x: number; y: number; w: number; h: number } };
};

export const SPACE_CARDS: SpaceCardDef[] = [
  { title: "AI Claymation and Wool Explainer Videos", blurb: "Any topic, a 10-second clay, wool or Pixar-style video starring you", inputs: [{ img: IMG.mSelfie }], output: { img: IMG.mClay } },
  { title: "Shadow Clone", blurb: "Reference Video", inputs: [{ img: IMG.mOnModel }], output: { img: IMG.mShadow } },
  { title: "Product Multi-Angle Shots", blurb: "One product photo in, five studio angles out", inputs: [{ img: IMG.mMulti }], output: { img: IMG.mPack } },
  {
    title: "Product in Scene + Relight",
    blurb: "Drop your product into any scene with matching light",
    inputs: [
      { img: IMG.cakeSrc, crop: { x: 930, y: 470, w: 430, h: 430 } },
      { img: IMG.cakeMoon, crop: { x: 120, y: 260, w: 520, h: 520 } },
    ],
    output: { img: IMG.cakeMoon, crop: { x: 760, y: 300, w: 820, h: 620 } },
  },
  { title: "Product in Hand (UGC)", blurb: "Put your product in a creator's hand, selfie style", inputs: [{ img: IMG.mUgc }], output: { img: IMG.alt02, crop: { x: 420, y: 120, w: 760, h: 760 } } },
  { title: "Swap Product into a Reference Ad", blurb: "Use any ad you love as the template for your product", inputs: [{ img: IMG.mPhone }], output: { img: IMG.mSwap } },
  { title: "3×3 Product Ad Grid", blurb: "Nine ad concepts for your product in one image", inputs: [{ img: IMG.mPlace }], output: { img: IMG.mGrid } },
  {
    title: "Product Poster / Ad Creative",
    blurb: "Your product plus your headline, as a finished poster",
    inputs: [{ img: IMG.chairSrc, crop: { x: 30, y: 230, w: 720, h: 720 }, flip: true }],
    output: { img: IMG.chairPoster, crop: { x: 150, y: 120, w: 1460, h: 820 } },
  },
  { title: "Packaging from Dieline", blurb: "Turn a flat dieline into a finished 3D box shot", inputs: [{ img: IMG.mFlat }], output: { img: IMG.mPack } },
  {
    title: "Cinematic Ad Sequence",
    blurb: "Six storyboard frames for a product film",
    inputs: [{ img: IMG.cupSrc, crop: { x: 820, y: 470, w: 400, h: 400 }, flip: true }],
    output: { img: IMG.cupCafe, crop: { x: 380, y: 160, w: 1000, h: 700 } },
  },
  { title: "Product Placement Video", blurb: "Your product in any scene, as a 6-second video", inputs: [{ img: IMG.mUgc }], output: { img: IMG.mPlace } },
  { title: "Phone Photo to Studio Product Video", blurb: "From a messy phone snap to a studio turntable video", inputs: [{ img: IMG.mPhone }], output: { img: IMG.mExploded } },
];

export const SPACES_LAYOUT = {
  tabsY: 84,
  gridY: 146,
  cardW: 452,
  cardH: 300,
  gap: 16,
  bannerH: 210,
  height: 1720,
};

/** card index -> top-left in page space */
export const spaceCardPos = (i: number) => {
  const L = SPACES_LAYOUT;
  const row = Math.floor(i / 3);
  const col = i % 3;
  const extra = row >= 2 ? L.bannerH + L.gap : 0;
  return { x: PAD + col * (L.cardW + L.gap), y: L.gridY + row * (L.cardH + L.gap) + extra };
};

export const SpacesPage: React.FC<{
  highlight?: number[];
  lift?: number[];
  appear?: number[];
  logoLook?: { x: number; y: number };
}> = ({ highlight = [], lift = [], appear = [], logoLook }) => {
  const L = SPACES_LAYOUT;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: PAGE_W, height: L.height, background: C.ink, fontFamily: FONT.ui, transformStyle: "preserve-3d" }}>
      <div style={{ position: "absolute", left: 0, top: 0 }}>
        <NavBar width={PAGE_W} active="Spaces" logoLook={logoLook} />
      </div>
      <div style={{ position: "absolute", left: PAD, top: L.tabsY, width: INNER, display: "flex", alignItems: "center", gap: 8 }}>
        {["Recommended", "Community", "My spaces", "Favourites"].map((t, i) => (
          <div
            key={t}
            style={{
              padding: "8px 14px",
              borderRadius: 10,
              fontSize: 14,
              fontWeight: i === 0 ? 600 : 500,
              color: i === 0 ? C.text : C.textMuted,
              background: i === 0 ? C.layer3 : "transparent",
            }}
          >
            {t}
          </div>
        ))}
        <div style={{ flex: 1 }} />
        <div style={{ display: "flex", alignItems: "center", gap: 8, width: 200, height: 38, borderRadius: 10, background: C.layer1, border: `1px solid ${C.layer3}`, padding: "0 12px", color: C.textMuted, fontSize: 13 }}>
          <ISearch size={15} /> Search spaces
        </div>
        <div style={{ width: 38, height: 38, borderRadius: 10, background: C.layer1, border: `1px solid ${C.layer3}`, display: "flex", alignItems: "center", justifyContent: "center", color: C.textMuted }}>
          <ISliders size={16} />
        </div>
        <YellowBtn label="Create New Space" size="sm" icon={<IPlus size={15} color={C.ink} />} />
      </div>
      {SPACE_CARDS.map((c, i) => {
        const p = spaceCardPos(i);
        const a = appear[i] ?? 1;
        return (
          <div
            key={c.title}
            style={{
              position: "absolute",
              left: p.x,
              top: p.y,
              opacity: clamp01(a * 1.4),
              transform: `translateY(${(1 - E.outExpo(clamp01(a))) * 80}px)`,
            }}
          >
            <WorkflowCard
              inputs={c.inputs}
              output={c.output}
              title={c.title}
              blurb={c.blurb}
              width={L.cardW}
              highlight={highlight[i] ?? 0}
              lift={lift[i] ?? 0}
            />
          </div>
        );
      })}
      {/* custom workflow banner */}
      <div
        style={{
          position: "absolute",
          left: PAD,
          top: L.gridY + 2 * (L.cardH + L.gap),
          width: INNER,
          height: L.bannerH,
          borderRadius: 16,
          overflow: "hidden",
          background: "radial-gradient(90% 140% at 60% 0%, #1E3A8A 0%, #0F172A 45%, #0A0A0A 100%)",
          border: `1px solid ${C.line}`,
        }}
      >
        <div style={{ position: "absolute", left: 40, top: 56 }}>
          <Heading size={34}>Create your custom workflow</Heading>
          <div style={{ marginTop: 10, color: C.textSubtle, fontSize: 16 }}>Build node based generative workflows and bring your ideas to life</div>
          <div style={{ marginTop: 18 }}>
            <YellowBtn label="Explore now" size="sm" />
          </div>
        </div>
        <div style={{ position: "absolute", right: 70, top: 26, transform: "rotate(-4deg)", borderRadius: 14, overflow: "hidden", border: "3px solid #fff", boxShadow: "0 20px 40px rgba(0,0,0,0.5)" }}>
          <Photo img={IMG.cakeMoon} crop={{ x: 700, y: 250, w: 900, h: 620 }} width={250} height={170} />
        </div>
        <div
          style={{
            position: "absolute",
            right: 360,
            top: 64,
            width: 230,
            borderRadius: 12,
            border: "1.5px solid rgba(255,255,255,0.35)",
            background: "rgba(10,10,10,0.6)",
            color: C.textSubtle,
            fontFamily: FONT.mono,
            fontSize: 12,
            padding: 12,
            lineHeight: 1.5,
          }}
        >
          Ultra-realistic close-up product shot
        </div>
      </div>
    </div>
  );
};

// ===================================================================== WORKFLOW RUN PAGE

/** Crop of the cake photo used in the product slot (and as the canvas source node). */
export const WF_PRODUCT_CROP = { x: 905, y: 525, w: 460, h: 240 };
/** Page-space geometry of the run panel (used for camera targeting). */
export const WF = {
  header: { x: 38, y: 98, w: 368, h: 150 },
  product: { x: 38, y: 264, w: 368, h: 200 },
  productInner: { x: 46, y: 272, w: 352, h: 184 },
  scene: { x: 38, y: 478, w: 368, h: 140 },
  generate: { x: 38, y: 808, w: 368, h: 54 },
};

export const WorkflowPage: React.FC<{
  productFill?: number;
  sceneFill?: number;
  productHover?: number;
  generateP?: number;
  generatePress?: number;
  canvas?: React.ReactNode;
  logoLook?: { x: number; y: number };
}> = ({ productFill = 0, sceneFill = 0, productHover = 0, generateP = 0, generatePress = 0, canvas, logoLook }) => {
  const ready = clamp01(generateP);
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: PAGE_W, height: 900, background: C.ink, fontFamily: FONT.ui }}>
      <NavBar width={PAGE_W} active="Spaces" logoLook={logoLook} />
      {/* left run panel */}
      <div style={{ position: "absolute", left: PAD, top: 86, width: 392, height: 790, borderRadius: 18, background: C.layer1, border: `1px solid ${C.line}` }}>
        <div style={{ position: "absolute", left: 12, top: 12, width: 368, height: 150, borderRadius: 12, overflow: "hidden", background: "#121212" }}>
          <div style={{ position: "absolute", left: 18, top: 18, transform: "rotate(-6deg)", border: "2px solid #fff", borderRadius: 6, overflow: "hidden" }}>
            <Photo img={IMG.cakeSrc} crop={{ x: 930, y: 470, w: 430, h: 430 }} width={62} height={62} />
          </div>
          <div style={{ position: "absolute", left: 48, top: 54, transform: "rotate(5deg)", border: "2px solid #fff", borderRadius: 6, overflow: "hidden" }}>
            <Photo img={IMG.cakeMoon} crop={{ x: 120, y: 260, w: 520, h: 520 }} width={62} height={62} />
          </div>
          <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: 190 }}>
            <Photo img={IMG.cakeMoon} crop={{ x: 820, y: 220, w: 700, h: 720 }} width={190} height={150} />
          </div>
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(0,0,0,0.75), rgba(0,0,0,0) 55%)" }} />
          <div style={{ position: "absolute", left: 14, bottom: 14, fontWeight: 600, fontSize: 16, color: C.white }}>Product in Scene + Relight</div>
          <div style={{ position: "absolute", right: 12, top: 12, display: "flex", alignItems: "center", gap: 4, background: C.white, color: C.ink, borderRadius: 8, padding: "4px 9px", fontSize: 12, fontWeight: 600 }}>
            Switch <IChevronDown size={13} color={C.ink} />
          </div>
        </div>
        <div style={{ position: "absolute", left: 12, top: 178 }}>
          <UploadSlot
            label="Product photo"
            width={368}
            height={200}
            fillP={productFill}
            hover={productHover}
            filled={{ img: IMG.cakeSrc, crop: WF_PRODUCT_CROP, name: "cake.jpg" }}
          />
        </div>
        <div style={{ position: "absolute", left: 12, top: 392 }}>
          <UploadSlot
            label="Scene photo"
            width={368}
            height={140}
            fillP={sceneFill}
            filled={{ img: IMG.cakeMoon, crop: { x: 60, y: 160, w: 760, h: 520 }, name: "moon-surface.jpg" }}
          />
        </div>
        <div style={{ position: "absolute", left: 12, top: 548, width: 368, color: C.textMuted, fontSize: 12.5, lineHeight: 1.55 }}>
          Your label and colours stay exactly as in your photo. Result is upscaled 2x.
        </div>
        <div
          style={{
            position: "absolute",
            left: 12,
            bottom: 14,
            width: 368,
            height: 54,
            borderRadius: 12,
            background: ready > 0.5 ? C.yellow : C.layer3,
            color: ready > 0.5 ? C.ink : C.dim,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 12,
            fontWeight: 600,
            fontSize: 16,
            transform: `translateY(${clamp01(generatePress) * 3}px)`,
            boxShadow: ready > 0.5 ? `0 ${3 * (1 - clamp01(generatePress))}px 0 ${C.yellowEdge}, 0 0 ${40 * prog(ready, 0.5, 1)}px rgba(254,204,21,${0.35 * prog(ready, 0.5, 1)})` : "none",
          }}
        >
          Generate
          <span style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 13, opacity: 0.85 }}>◎ 2.76</span>
        </div>
      </div>
      {/* right overview panel */}
      <div style={{ position: "absolute", left: PAD + 392 + 18, top: 86, width: PAGE_W - PAD * 2 - 392 - 18, height: 790, borderRadius: 18, background: C.layer1, border: `1px solid ${C.line}`, overflow: "hidden" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "14px 16px" }}>
          {["Overview", "Templates", "Generations"].map((t, i) => (
            <div key={t} style={{ padding: "7px 12px", borderRadius: 9, fontSize: 14, fontWeight: i === 0 ? 600 : 500, color: i === 0 ? C.text : C.textMuted, background: i === 0 ? C.layer3 : "transparent" }}>
              {t}
            </div>
          ))}
          <div style={{ flex: 1 }} />
          <IHeart size={17} color={C.textMuted} />
          <div style={{ width: 10 }} />
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: C.textSubtle, fontSize: 14 }}>
            <IShare size={16} color={C.textSubtle} /> Share
          </div>
        </div>
        <div style={{ position: "absolute", left: 16, right: 16, top: 62, height: 470, borderRadius: 14, background: C.ink, overflow: "hidden", backgroundImage: "radial-gradient(rgba(255,255,255,0.08) 1px, transparent 1px)", backgroundSize: "18px 18px" }}>
          {canvas}
        </div>
        <div style={{ position: "absolute", left: 16, right: 16, top: 548, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 18px", borderRadius: 14, background: C.layer2 }}>
          <div style={{ fontSize: 22, fontWeight: 600, color: C.yellowText }}>Product in Scene + Relight</div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, background: "#3a3218", color: C.yellowText, borderRadius: 10, padding: "9px 18px", fontWeight: 600, fontSize: 14 }}>
            <ILock size={14} color={C.yellowText} /> Remix
          </div>
        </div>
        <div style={{ position: "absolute", left: 16, right: 16, top: 640, padding: "14px 18px", borderRadius: 14, border: `1px solid ${C.line}`, color: C.textSubtle, fontSize: 13.5, lineHeight: 1.6 }}>
          <div style={{ color: C.text, fontWeight: 600, marginBottom: 6 }}>Details</div>
          Turn a plain packshot into lifestyle product photography. Upload a product photo and a photo of the scene you want, and this space places your product in the scene and relights it to match the light direction, colour and shadows.
        </div>
      </div>
    </div>
  );
};
