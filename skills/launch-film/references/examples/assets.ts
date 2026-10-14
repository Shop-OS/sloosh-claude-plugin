import { staticFile } from "remotion";

export type ImgAsset = { src: string; w: number; h: number; mock?: boolean };

// Logical sizes are the production-pack pixel sizes; "hd/" files are 2x Lanczos
// upscales of the same frames so zoomed match cuts stay crisp.
const pack = (name: string, h = 941): ImgAsset => ({ src: staticFile(`pack/${name}.png`), w: 1672, h });
const hd = (name: string, h = 941): ImgAsset => ({ src: staticFile(`hd/${name}.jpg`), w: 1672, h });
const mock = (name: string, w = 1200, h = 900): ImgAsset => ({
  src: staticFile(`mock/${name}.jpg`),
  w,
  h,
  mock: true,
});

export const IMG = {
  // Story images (ASSET_SCRIPT_GUIDE.md)
  cakeSrc: hd("I10_Baker_Original_Cake"),
  cakeMoon: hd("I17_FINAL_Cake_On_Moon"),
  cupSrc: hd("I11_Photographer_Original_Cup", 940),
  cupCafe: hd("I18_FINAL_Correct_Cup_Cafe", 940),
  chairSrc: hd("I12_Designer_Original_Chair"),
  chairPoster: hd("I19_FINAL_Minimal_Chair_Poster"),
  alt01: hd("ALT01_Cake_Moon_With_Baker"),
  alt02: hd("ALT02_Photographer_Drinking_Cup", 940),
  alt03: hd("ALT03_Chair_Poster_With_Designer"),
  // Clean plates (poster headline painted out) so cropped formats can carry re-typeset copy
  chairPosterClean: { src: staticFile("hd/I19_clean.jpg"), w: 1672, h: 941 },
  alt03Clean: { src: staticFile("hd/ALT03_clean.jpg"), w: 1672, h: 941 },
  bakerLaptop: pack("I16_Baker_Repeated_Correction"),
  handover: pack("I20_Baker_Customer_Handover"),
  commission: pack("I21_Photographer_New_Commission"),
  approval: pack("I22_Designer_Client_Approval"),
  nextCake: pack("I23_Baker_Next_Cake"),
  stroke: pack("I24_Fresh_Stroke_Endcard_Background"),
  digital: pack("I09_Digital_Artist"),
  landscape: pack("I05_Landscape_Painter"),
  impasto: pack("I06_Expressive_Impasto"),
  print: pack("I07_Printed_Illustration"),
  photographer: pack("I08_Early_Photographer"),
  studio: pack("I04_Portrait_Studio"),
  eye: pack("I03_Painted_Portrait_Eye"),
  cave: pack("I02_Cave_Drawing_Recognition"),
  pigment: pack("I01_Pigment_On_Stone"),
  // Mock placeholders (replace later)
  mClay: mock("mock_claymation"),
  mShadow: mock("mock_shadow_clone"),
  mMulti: mock("mock_multi_angle"),
  mUgc: mock("mock_ugc"),
  mSwap: mock("mock_swap_ad"),
  mGrid: mock("mock_ad_grid"),
  mPack: mock("mock_packaging"),
  mPlace: mock("mock_placement"),
  mPhone: mock("mock_phone_studio"),
  mExploded: mock("mock_exploded"),
  mTryOn: mock("mock_tryon"),
  mTryOnB: mock("mock_try_on_b"),
  mFlat: mock("mock_flatlay"),
  mEditorial: mock("mock_editorial"),
  mFashion: mock("mock_fashion"),
  mOnModel: mock("mock_on_model"),
  mJewel: mock("mock_jewellery"),
  mSelfie: mock("mock_selfie_studio"),
  mHero: mock("mock_hero", 1800, 760),
  rWarm: mock("mock_relight_warm", 1280, 720),
  rCool: mock("mock_relight_cool", 1280, 720),
  rGolden: mock("mock_relight_golden", 1280, 720),
  rMono: mock("mock_relight_mono", 1280, 720),
  rDusk: mock("mock_relight_dusk", 1280, 720),
  rClose: mock("mock_relight_close", 900, 900),
} satisfies Record<string, ImgAsset>;

export type ImgKey = keyof typeof IMG;

// Product bounding boxes in logical pixels (measured on gridded proofs).
export const PRODUCT = {
  cakeSrc: { x: 965, y: 532, w: 347, h: 233, cx: 1138, cy: 670 },
  cakeMoon: { x: 983, y: 510, w: 372, h: 255, cx: 1169, cy: 665 },
  // cup bodies (no handle); source is shown mirrored so the handle sides match
  cupSrc: { x: 545, y: 573, w: 160, h: 167, cx: 625, cy: 657 },
  cupCafe: { x: 825, y: 333, w: 283, h: 307, cx: 966, cy: 487 },
  // chairs; source mirrored so both face right
  chairSrc: { x: 910, y: 255, w: 735, h: 670, cx: 1278, cy: 590 },
  chairPoster: { x: 222, y: 262, w: 728, h: 588, cx: 586, cy: 556 },
};
