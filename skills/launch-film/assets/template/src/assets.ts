import { staticFile } from "remotion";

export type ImgAsset = { src: string; w: number; h: number; mock?: boolean };

// Logical size = the original pixel size of the delivered image. `hd/` files are 2x
// Lanczos upscales; crops/measurements always use logical pixels.
export const pack = (file: string, w: number, h: number): ImgAsset => ({ src: staticFile(`pack/${file}`), w, h });
export const hd = (file: string, w: number, h: number): ImgAsset => ({ src: staticFile(`hd/${file}`), w, h });
export const mock = (file: string, w = 1200, h = 900): ImgAsset => ({ src: staticFile(`mock/${file}`), w, h, mock: true });
export const clip = (file: string) => staticFile(`clips/${file}`);

export const IMG = {
  // hero: hd("I10_hero.jpg", 1672, 941),
} satisfies Record<string, ImgAsset>;

// Measured object boxes (logical px) for match cuts — fill from gridify.py proofs.
export const BOX = {
  // cake: { x: 965, y: 532, w: 347, h: 233, cx: 1138, cy: 670 },
};
