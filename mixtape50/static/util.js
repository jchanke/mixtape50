/**
 * Cleans the title by:
 *  - Removing substrings enclosed in (...) or [...]
 *  - Removing " - " and everything after
 *  - Removing " feat.", " ft.", or " featuring" and everything after
 */
function cleanTitle(title) {
  // Remove substrings in parentheses or brackets
  // e.g. "Hello (Remix)" -> "Hello"
  title = title.replace(/\s+\(.+\)/g, "");
  title = title.replace(/\s+\[.+\]/g, "");

  // Remove " - " and everything after
  // e.g. "Hello - Extra Info" -> "Hello"
  title = title.replace(/ - .*/, "");

  // Remove " feat.", " ft.", or " featuring" (and subsequent text)
  // e.g. "Song ft. Artist" -> "Song"
  title = title.replace(/\W+(ft[:.]?|feat[:.]|featuring)\s.*/g, "");

  return title;
}

/**
 * Removes punctuation by:
 *  - Deleting XML escape sequences (&amp; &quot; &lt; &gt; &apos;)
 *  - Replacing slashes ("/", "//") and surrounding whitespace with " "
 *  - Replacing "&" and surrounding whitespace with " and "
 *  - Removing various punctuation characters
 *  - Trimming extra whitespace
 */
function removePunctuation(title) {
  title = title.replace(/&(?:amp|quot|lt|gt|apos);/g, "");
  title = title.replace(/\s*\/+\s*/g, " ");
  title = title.replace(/\s*&\s*/g, " and ");
  title = title.replace(/[!"#$%'‘’“”()*+,\-.:;<=>?@\[\]\\^_—`{|}~]/g, "");
  title = title.replace(/\s{2,}/g, " ");
  return title.trim();
}

/**
 * Sleeps for a given amount of time.
 * @param {number} time The time to sleep in milliseconds
 * @returns {Promise} A promise that resolves after the given time
 */
async function sleep(time) {
  return new Promise(resolve => setTimeout(resolve, time));
}

// Exporting the functions if needed (e.g., in a module environment)
export { cleanTitle, removePunctuation, sleep };