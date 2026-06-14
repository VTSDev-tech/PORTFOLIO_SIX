// ==========================================
// 1. GSAP CONFIGURATION & PLUGINS REGISTER
// ==========================================
gsap.registerPlugin(ScrollTrigger);

// ==========================================
// 2. CUSTOM CURSOR & BUBBLE TRAIL EFFECT
// ==========================================
const cursor = document.getElementById('custom-cursor');
const cursorDot = cursor.querySelector('.cursor-dot');
const cursorRing = cursor.querySelector('.cursor-ring');

let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;

window.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
  
  // Instant dot movement
  gsap.to(cursorDot, {
    x: mouseX,
    y: mouseY,
    duration: 0.05
  });

  // Smooth ring trailing
  gsap.to(cursorRing, {
    x: mouseX,
    y: mouseY,
    duration: 0.2,
    ease: "power2.out"
  });
});

// Cursor hover active state
const interactables = document.querySelectorAll('a, button, .work-card, .timeline-content, .resume-skill-box, .resume-footer-item, .book-sheet, .book-nav-btn, .progress-dot');
interactables.forEach(item => {
  item.addEventListener('mouseenter', () => {
    document.body.classList.add('cursor-hover');
  });
  item.addEventListener('mouseleave', () => {
    document.body.classList.remove('cursor-hover');
  });
});

// ==========================================
// 3. GSAP MAGNETIC BUTTON EFFECT
// ==========================================
const magneticElements = document.querySelectorAll('.magnetic-target');
magneticElements.forEach(el => {
  el.addEventListener('mousemove', (e) => {
    const bound = el.getBoundingClientRect();
    const x = e.clientX - bound.left - bound.width / 2;
    const y = e.clientY - bound.top - bound.height / 2;
    
    gsap.to(el, {
      x: x * 0.35,
      y: y * 0.35,
      duration: 0.3,
      ease: "power2.out"
    });
  });
  
  el.addEventListener('mouseleave', () => {
    gsap.to(el, {
      x: 0,
      y: 0,
      duration: 0.6,
      ease: "elastic.out(1, 0.3)"
    });
  });
});


// ==========================================
// 4. MUSIC & SOUND LOGIC
// ==========================================
const bgAudio = document.getElementById('bg-audio');
const audioToggle = document.getElementById('audio-toggle');

audioToggle.addEventListener('click', () => {
  if (bgAudio.paused) {
    bgAudio.play()
      .then(() => {
        audioToggle.classList.remove('off');
        audioToggle.innerText = "SOUND ON";
      })
      .catch(err => console.log("Blocked by autoplay browser policy"));
  } else {
    bgAudio.pause();
    audioToggle.classList.add('off');
    audioToggle.innerText = "SOUND OFF";
  }
});

// Intro screen dismiss with Smart Animate transition
const introScreen = document.getElementById('intro-screen');
const enterSiteBtn = document.getElementById('enter-site-btn');

enterSiteBtn.addEventListener('click', () => {
  // Prevent double clicks
  enterSiteBtn.style.pointerEvents = 'none';
  
  // Create Transition Timeline (Smart Animate)
  const transitionTimeline = gsap.timeline();

  // 1. Flash and hide the Enter button, show loading UI
  transitionTimeline.to(enterSiteBtn, {
    opacity: 0,
    duration: 0.2,
    onComplete: () => {
      enterSiteBtn.style.display = 'none';
      document.getElementById('intro-loading-ui').style.display = 'flex';
    }
  });

  // 2. Animate loading bar (Fake loading)
  const loadObj = { val: 0 };
  transitionTimeline.to(loadObj, {
    val: 100,
    duration: 1.5,
    ease: "power2.inOut",
    onUpdate: () => {
      document.getElementById('loading-fill').style.width = loadObj.val + '%';
      document.getElementById('loading-text').innerText = 'LOADING ' + Math.round(loadObj.val) + '%';
    }
  });

  // 3. Play sound right before transition
  transitionTimeline.call(() => {
    bgAudio.play()
      .then(() => {
        audioToggle.classList.remove('off');
        audioToggle.innerText = "SOUND ON";
      })
      .catch(() => console.log("Autoplay blocked"));
  });

  // 4. Smart Animate slide out
  // Slide up and fade out the center text and loading UI
  transitionTimeline.to('.intro-center', {
    y: -80,
    opacity: 0,
    duration: 0.8,
    ease: "power2.in"
  }, "+=0.2");

  // Zoom and fade out the background image
  transitionTimeline.to('.intro-bg-image', {
    scale: 1.1,
    opacity: 0,
    duration: 1.2,
    ease: "power2.inOut"
  }, 0.15);

  // Slide up the intro screen container itself
  transitionTimeline.to(introScreen, {
    y: "-100%",
    duration: 1.2,
    ease: "power3.inOut"
  }, 0.15);

  // 4. Simultaneously animate the entrance of the main portfolio content
  // Call simplified entrance animations at t = 0.5s (mid-way through slide up)
  transitionTimeline.call(runEntranceAnimations, null, 0.5);

  // 5. Cleanup: set display none to completely remove it from render tree
  transitionTimeline.set(introScreen, {
    display: 'none'
  });
});


// ==========================================
// 5. THREE.JS 3D HYPER-REALISTIC JELLYFISH
// ==========================================
// 3D Jellyfish Background code removed

// ==========================================
// 6. GSAP ANIMATIONS & DEEP-DIVE SCROLL
// ==========================================

function runEntranceAnimations() {
  // Smoothly slide down nav bar
  gsap.from('nav', {
    y: -40,
    opacity: 0,
    duration: 1.0,
    ease: "power3.out"
  });

  // Smoothly slide up the main resume card as a unified element (Smart Animate style)
  gsap.from('.resume-card-container', {
    y: 60,
    opacity: 0,
    duration: 1.2,
    ease: "power3.out"
  });

  // Fade in scroll indicator
  gsap.from('.scroll-indicator', {
    opacity: 0,
    duration: 1.0,
    delay: 0.6
  });
}

function initGSAPScroll() {
  const isDesktop = window.innerWidth > 900;
  
  // Ambient focus for Chronicle Book
  gsap.to('.water-rays', {
    opacity: 0.1,
    scrollTrigger: {
      trigger: '#chronicle-book',
      start: "top center",
      end: "bottom center",
      toggleActions: "play reverse play reverse"
    }
  });

  // Background dust generator for library feel
  setInterval(() => {
    if (Math.random() > 0.5) {
      const dust = document.createElement('div');
      dust.className = 'ambient-dust';
      dust.style.position = 'fixed';
      dust.style.left = `${Math.random() * window.innerWidth}px`;
      dust.style.top = `${window.innerHeight + 10}px`;
      dust.style.width = `${Math.random() * 3 + 1}px`;
      dust.style.height = dust.style.width;
      dust.style.background = '#00f5d4';
      dust.style.borderRadius = '50%';
      dust.style.pointerEvents = 'none';
      dust.style.zIndex = '0';
      dust.style.boxShadow = '0 0 8px #00f5d4';
      document.body.appendChild(dust);

      gsap.to(dust, {
        y: -window.innerHeight - 50,
        x: `+=${(Math.random() - 0.5) * 200}`,
        opacity: Math.random() * 0.4 + 0.1,
        duration: Math.random() * 10 + 10,
        ease: "none",
        onComplete: () => dust.remove()
      });
    }
  }, 300);

  // 2. Wave Float effect on cards
  const cards = document.querySelectorAll('.work-card');
  cards.forEach((card, index) => {
    // Parallax slide-in reveal
    gsap.from(card.querySelector('.work-visual'), {
      opacity: 0,
      scale: 0.95,
      x: index % 2 === 0 ? -60 : 60,
      duration: 1,
      scrollTrigger: {
        trigger: card,
        start: "top 80%",
        end: "top 45%",
        scrub: 1
      }
    });

    gsap.from(card.querySelector('.work-details'), {
      opacity: 0,
      y: 50,
      duration: 1,
      scrollTrigger: {
        trigger: card,
        start: "top 85%",
        end: "top 50%",
        scrub: 1
      }
    });

    // Floating wavy loop
    gsap.to(card, {
      y: "+=12",
      duration: 3.2 + index * 0.8,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut"
    });
  });


  // Awards Timeline reveal
  const timelineItems = document.querySelectorAll('.timeline-item');
  timelineItems.forEach((item, index) => {
    gsap.from(item.querySelector('.timeline-content'), {
      opacity: 0,
      x: 30,
      duration: 0.8,
      scrollTrigger: {
        trigger: item,
        start: "top 80%",
        toggleActions: "play none none reverse"
      }
    });
  });



  // Banner image fade and subtle zoom reveal
  const banners = document.querySelectorAll('.banner-section');
  banners.forEach((banner) => {
    const img = banner.querySelector('.banner-img');
    if (img) {
      gsap.from(img, {
        opacity: 0,
        scale: 0.95,
        duration: 1.2,
        ease: "power2.out",
        scrollTrigger: {
          trigger: banner,
          start: "top 85%",
          toggleActions: "play none none reverse"
        }
      });
    }
  });

  // Cinematic banner fade and subtle zoom reveal
  gsap.from('.cinematic-img', {
    opacity: 0,
    scale: 0.95,
    duration: 1.2,
    ease: "power2.out",
    scrollTrigger: {
      trigger: ".cinematic-section",
      start: "top 85%",
      toggleActions: "play none none reverse"
    }
  });

  // Character and Environment design sheets reveal
  const sheets = document.querySelectorAll('.char-sheet-section, .env-sheet-section, .artbook-section');
  sheets.forEach((sheet) => {
    const container = sheet.querySelector('.char-sheet-container, .env-sheet-container, .artbook-container');
    if (container) {
      gsap.from(container, {
        opacity: 0,
        y: 40,
        scale: 0.98,
        duration: 1.0,
        ease: "power2.out",
        scrollTrigger: {
          trigger: sheet,
          start: "top 85%",
          toggleActions: "play none none reverse"
        }
      });
    }
  });


  // Navigation ScrollSpy (active link switching on scroll)
  const navLinks = document.querySelectorAll('.nav-links a');
  const sectionsToSpy = document.querySelectorAll('section[id]');
  
  sectionsToSpy.forEach((section) => {
    ScrollTrigger.create({
      trigger: section,
      start: "top 35%",
      end: "bottom 35%",
      onToggle: (self) => {
        if (self.isActive) {
          const id = section.getAttribute('id');
          navLinks.forEach((link) => {
            if (link.getAttribute('href') === `#${id}`) {
              link.classList.add('active');
            } else {
              link.classList.remove('active');
            }
          });
        }
      }
    });
  });
}


// ==========================================
// 8. TICK LOOP (THREE.JS RENDER LOOP)
// ==========================================
// Render loop removed


// ==========================================
// 10. INTERACTIVE 3D FLIPBOOK (CHRONICLE)
// ==========================================
function initChronicleBook() {
  const flipbook = document.getElementById('flipbook');
  if (!flipbook) return;

  const sheets = flipbook.querySelectorAll('.book-sheet');
  const chronicleBookSection = document.getElementById('chronicle-book');

  let currentSheetIndex = 0; 
  const maxSheets = sheets.length; 

  // Update book state and z-index layering
  function updateBookState() {
    sheets.forEach((sheet, index) => {
      if (index < currentSheetIndex) {
        // Flipped to the left side
        sheet.classList.add('flipped');
        // Left pages stack upwards from the bottom (index 0 is at bottom, current-1 is on top)
        sheet.style.zIndex = index + 1;
      } else {
        // Not flipped (stays on the right side)
        sheet.classList.remove('flipped');
        // Right pages stack downwards (first page index `current` is on top, max-1 is at bottom)
        sheet.style.zIndex = maxSheets - index;
      }
    });

    // Dynamic centering for smaller screens
    if (window.innerWidth <= 900) {
      if (currentSheetIndex === 0) {
        // Closed, showing front cover (right half)
        gsap.to(flipbook, { xPercent: -25, duration: 0.5, ease: "power2.out" });
      } else if (currentSheetIndex === maxSheets) {
        // Closed, showing back cover (left half)
        gsap.to(flipbook, { xPercent: 25, duration: 0.5, ease: "power2.out" });
      } else {
        // Open, showing both pages
        gsap.to(flipbook, { xPercent: 0, duration: 0.5, ease: "power2.out" });
      }
    } else {
      gsap.to(flipbook, { xPercent: 0, duration: 0.5 });
    }

    // Cinematic Text Reveal for newly exposed pages
    const newActiveTexts = [];
    if (currentSheetIndex > 0) {
      newActiveTexts.push(...sheets[currentSheetIndex - 1].querySelectorAll('.page-back .page-text, .page-back .page-heading, .page-back .page-divider, .page-back .page-character-name, .cover-title, .cover-quote, .closing-seal-trans'));
    }
    if (currentSheetIndex < maxSheets) {
      newActiveTexts.push(...sheets[currentSheetIndex].querySelectorAll('.page-front .page-text, .page-front .page-heading'));
    }
    
    if (newActiveTexts.length > 0) {
      gsap.fromTo(newActiveTexts, 
        { opacity: 0, y: 15, filter: "blur(4px)" }, 
        { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.0, stagger: 0.05, ease: "power2.out", overwrite: "auto" }
      );
    }
  }

  // Next sheet flip
  function nextSheet() {
    if (currentSheetIndex < maxSheets) {
      currentSheetIndex++;
      updateBookState();
    }
  }

  // Prev sheet flip
  function prevSheet() {
    if (currentSheetIndex > 0) {
      currentSheetIndex--;
      updateBookState();
    }
  }

  // Bind clicks directly to the book sheets
  sheets.forEach((sheet) => {
    sheet.addEventListener('click', () => {
      // If the sheet is on the left (flipped), flip it back to the right
      if (sheet.classList.contains('flipped')) {
        prevSheet();
      } else {
        // If the sheet is on the right (not flipped), flip it to the left
        nextSheet();
      }
    });
  });

  // Bind key presses (only when book is in view)
  window.addEventListener('keydown', (e) => {
    const bookRect = chronicleBookSection.getBoundingClientRect();
    const isInViewport = bookRect.top < window.innerHeight && bookRect.bottom > 0;
    if (!isInViewport) return;

    if (e.key === 'ArrowRight') {
      nextSheet();
    } else if (e.key === 'ArrowLeft') {
      prevSheet();
    }
  });

  // Breathing Book Animation
  gsap.to(flipbook, {
    y: -8,
    duration: 3.5,
    repeat: -1,
    yoyo: true,
    ease: "sine.inOut"
  });

  // Interactive Image Parallax
  const imageSlots = document.querySelectorAll('.page-image-slot');
  imageSlots.forEach(slot => {
    slot.addEventListener('mousemove', (e) => {
      const rect = slot.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      const img = slot.querySelector('.page-illustration');
      if(img) {
        gsap.to(img, {
          x: x * -0.05,
          y: y * -0.05,
          scale: 1.05,
          rotationY: x * 0.03,
          rotationX: -y * 0.03,
          duration: 0.4,
          ease: "power2.out"
        });
      }
    });
    slot.addEventListener('mouseleave', () => {
      const img = slot.querySelector('.page-illustration');
      if(img) {
        gsap.to(img, {
          x: 0, y: 0, scale: 1, rotationY: 0, rotationX: 0, duration: 0.8, ease: "power2.out"
        });
      }
    });
  });

  // Init state
  updateBookState();
}

// ==========================================
// 9. WINDOW DOM INTEGRATION
// ==========================================
window.addEventListener('DOMContentLoaded', () => {
  initGSAPScroll();
  initChronicleBook();
});

