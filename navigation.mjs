// Open the target and every enclosing disclosure before scrolling to a fragment.
export function revealFragment(document, hash, scroll = true) {
  let id;
  try { id = decodeURIComponent((hash || '').replace(/^#/, '')); }
  catch { return false; }
  if (!id) return false;
  const target = document.getElementById(id);
  if (!target) return false;
  for (let element = target; element; element = element.parentElement) {
    if (element.tagName === 'DETAILS') element.open = true;
  }
  if (scroll) target.scrollIntoView({ block: 'start' });
  return true;
}
