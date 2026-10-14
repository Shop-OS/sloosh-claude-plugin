# Engine API (assets/template/src)

## Contents
1. Project layout
2. lib/anim.ts
3. components/MotionBlur.tsx
4. components/Stage3D.tsx + lib/project.ts
5. components/Tech.tsx
6. components/FX.tsx
7. components/Media.tsx
8. components/Cursor.tsx
9. lib/cropCamera.ts
10. SoundTrack.tsx, cues.ts, sfxPeaks.ts
11. recipes/*
12. Composition structure for multi-part films

## 1. Layout
```
src/
  theme.ts timeline.ts assets.ts cues.ts sfxPeaks.ts SoundTrack.tsx Film.tsx Root.tsx index.ts
  components/  MotionBlur Stage3D Tech FX Media Cursor
  lib/         anim project cropCamera
  recipes/     PunctuationWord SplitWordWindow RailWord ContactSheet Sketch DetailWindows ChatBox MosaicWall
  scenes/      one file per scene (yours)
```

## 2. `lib/anim.ts`
- `E` easings: `outExpo outQuart outCubic inOutCubic inOutQuart inOutQuint inOutExpo inExpo inCubic outBack outBackSoft linear`.
- `prog(t, t0, t1, ease?)` → clamped eased 0..1. `kf(t, times[], values[], ease?)` → clamped multi-key.
- `path(t, keys, field)` piecewise camera path (easing on destination key `e`); `pathSpeed(t, keys, fields)` units/sec.
- `mix(a,b,p)`, `clamp01`, `hash(n)` deterministic noise.

## 3. `MotionBlur`
`<MotionBlur samplesAt={(fr) => n} smearAt={(fr) => ({x, y})} shutterAngle={180}>` — trailing
shutter, `n` sub-frame `Freeze` copies blended with plus-lighter; `smearAt` adds an axis-aligned
gaussian. Children must read `useCurrentFrame()` themselves (they receive fractional frames).

## 4. 3D stage
- `<Stage3D perspective={1500} background>` → `<Plane3D cam={{tx,ty,z,rx,rz,ry?,sx?,sy?}} width height>` page content `</Plane3D>`.
- Children of `Plane3D` keep 3D (`transformStyle: preserve-3d`): lift with `translateZ(h)`;
  billboard with `rotateZ(-rz) rotateX(-rx*0.85)`.
- `project(cam, px, py, pz?, perspective?)` → screen `{x, y, scale}` for cursors, tags and
  2D overlays pinned to page points.

## 5. `Tech` (editorial overlays; colours from theme `C.accent/ink/paperLine/text/white`)
`MonoLabel{text,p,size,color,weight,caret}` · `Tag{text,p,bg,color,size}` ·
`Crosshair{x,y,size,color,p,ring,thickness}` ·
`BBox{x,y,w,h,p,color,handle,handleFill,label,labelPos,tagBg,tagColor,labelSize,dashed}` ·
`Guides{xs,ys,p,origin,color,thickness,squares,squareColor,squareSize,squareP}` ·
`Connector{d,p,color,width,dashed}` · `Ruler{x,y,length,vertical,p,color,step}`.

## 6. `FX`
`ChromaSplit{amount, angle}` (2-frame RGB split; unique filter id) ·
`PixelWipe{p,color,cell,mode:'cover'|'reveal',dir,seed,softness,accent,accentRatio}` ·
`TiltShift{top,bottom,blur}` (backdrop-filter bands).

## 7. `Media`
`Photo{img,width,height,crop,flip,radius}` (cover-fit a crop rect) ·
`Placed{img,scale,x,y,flip}` · `ClipView{src,clipW,clipH,width,height,crop,trimBefore,playbackRate,flip}`
(video through a crop rect; muted) · `Zoom{k,cx,cy,dx,dy}` · `Grain{opacity}` ·
`Vignette{strength}` · `Flash{o,color}`.

## 8. `Cursor`
`Cursor{x,y,size,press,ripple,rippleColor,opacity}`; `bez(t,p0,p1,p2,p3)` for curved paths.

## 9. `lib/cropCamera.ts`
`viewOf(placement, k, cx, cy)`, `mapView(view, from, to)`, `toScreen(view, px, py)`,
`rectToScreen(view, rect)`, `lerpRect`, `fullView(placement)`,
`makePair(placementA, placementB, focus)` → `{view(k), viewB(k)}` — paste placements from
`scripts/align_pair.py`.

## 10. Sound
- `sfxPeaks.ts` (generated): `SFX_PEAKS[name] = peak seconds`.
- `cues.ts`: `Cue{ s, at, v, label }` — `at` = frame of the peak.
- `<SoundTrack vo={[{name, src, from, gain?}]} cues={CUES} speech={speechFrom(VO)} trim duck offset />`.
  `offset` shifts a part's cue sheet when the part sits inside a longer film.

## 11. Recipes
- `PunctuationWord{text,bg,color,size,dur,label}`
- `SplitWordWindow{left,right,images,bg,color,size,every,window,tagPrefix}`
- `RailWord{word,size,bg,color,lit,run0,run1,collapse0,collapse1}` (+children overlay)
- `ContactSheet{tiles:[{img,crop,label}],bg,ink,tile,gap,expand0,expand1,expandTo,tag,note}`
- `Sketch`: `Stroke{d,p,w,color}`, `Sparkle{x,y,s}`, `Handwriting{p,size,color}`,
  `CakeMoonSketch{moon,top,body,plate,piping,berries[],stars[]}` + `CAKE_SKETCH_BOX`
- `DetailWindows{img,view,windows:[{r,label,at,chip}],dim,readout:{title,rows,at}}`
- `ChatBox`: `ChatWindow`, `UserBubble{text,p,img}`, `AiResult{img,reveal,caption}`,
  `Composer{text,p,sendPress}`, `ChatButton{label,press,icon}`, `XTag{text,p}` (generic,
  unbranded — never imitate a real product)
- `MosaicWall{items,cols,rows,cell,gap,zoom(f),reveal(f),glitch(f)}`

## 12. Multi-part films
```tsx
// Root.tsx
<Composition id="Part1" component={Part1} durationInFrames={P1.dur} fps={30} width={1920} height={1080} />
…
<Composition id="FullFilm" component={FullFilm} durationInFrames={ALL} … />
// FullFilm.tsx — sequence the parts; each part keeps its own SoundTrack (VO + cues) inside
<Sequence from={0} durationInFrames={P1.dur}><Part1 /></Sequence>
<Sequence from={P1.dur} durationInFrames={P2.dur}><Part2 /></Sequence>
```
Because each part's audio lives inside its own component, sequencing parts keeps VO and
SFX in sync automatically. Give parts an `endCard` prop so intermediate end cards can be
dropped in the full film.
