import {imageSizes} from './image-sizes.mjs';
// Only reviewed, verified images can be used by screen or print.
export const imageMap=Object.fromEntries(Object.entries(imageSizes).map(([id,image])=>[id,image?.print??null]));
export const editorialNotes={};
