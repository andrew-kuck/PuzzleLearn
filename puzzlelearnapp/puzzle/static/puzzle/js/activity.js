
const overallStartTime = performance.now();

function getFormattedTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;

  // Pad minutes to 2 digits, format seconds to 2 decimal places with padding
  const paddedMinutes = String(minutes).padStart(2, '0');
  const paddedSeconds = seconds < 10 ? `0${seconds.toFixed(2)}` : seconds.toFixed(2);

  return `${paddedMinutes}:${paddedSeconds}`;
}

function activityComplete(customText=null) {
    setTimeout(() => {
        const endTime = performance.now();
        const duration = (endTime - overallStartTime) / 1000;
        let text = `Activity Complete in ${getFormattedTime(duration)}!`;
        if (customText !== null) {
            text += ` ${customText}`;
        }
        alert(text);
        history.back();
    }, 500);
}

function autoZoomHtml(extraVertical = 0) {
    const htmlEl = document.documentElement;

    // Reset html zoom to 1 to measure the true unscaled content dimensions
    htmlEl.style.zoom = "1";

    // Fallback baseline dimensions
    let maxRight = window.innerWidth;
    let maxBottom = window.innerHeight;

    // Scan all child elements inside the body to determine the content boundary
    const allElements = document.querySelectorAll('body *');
    allElements.forEach(el => {
        const rect = el.getBoundingClientRect();
        // Ignore invisible elements
        if (rect.width === 0 && rect.height === 0) return;
        
        if (rect.right > maxRight) maxRight = rect.right;
        if (rect.bottom > maxBottom) maxBottom = rect.bottom;
    });

    // Add additional vertical padding before scaling
    maxBottom += extraVertical;

    // Compute the scaling ratios
    const scaleX = window.innerWidth / maxRight;
    const scaleY = window.innerHeight / maxBottom;

    // Choose the smaller ratio to fit the content cleanly in both directions
    let finalScale = Math.min(scaleX, scaleY);

    // EXTRA ZOOM BUFFER: Multiplier less than 1.0 zooms out further
    // 0.95 adds a 5% safety margin around your content edges
    const zoomBufferMultiplier = 0.95;
    finalScale = finalScale * zoomBufferMultiplier;

    // Apply zoom directly to the root <html> element
    htmlEl.style.zoom = finalScale;
}

function autoZoom(extraVertical = 0) {
    // 1. Inject CSS rules onto the html element, leaving body styles untouched
    const style = document.createElement('style');
    style.textContent = `
        html {
            width: 100% !important;
            height: 100vh !important;
            overflow: hidden !important; /* Disables page-level scrollbars */
            transform-origin: top left !important; /* Anchors the zoom scale */
        }
    `;
    document.head.appendChild(style);

    // 2. Event Listeners for execution
    window.addEventListener('load', () => autoZoomHtml(extraVertical));
    window.addEventListener('resize', () => autoZoomHtml(extraVertical));

    // Run immediately if injected post-load
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        autoZoomHtml(extraVertical);
    }
}

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (const cookie of cookies) {
    const trimmed = cookie.trim();

    if (trimmed.startsWith(name + "=")) {
        return decodeURIComponent(trimmed.substring(name.length + 1));
    }
    }

    return "";
}





