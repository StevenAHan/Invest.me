window.scrollBy(0, 100);

gsap.fromTo('.banner-title', {opacity: 0}, {duration: 1.5, opacity: 1})

gsap.fromTo('.prompt-container', {y: -100, opacity: 0}, {y: 0, delay: 1, duration: 1, opacity: 1})
gsap.fromTo('.inline-wrapper', {y: -100, opacity: 0}, {y: 0, delay: 1, duration: 1, opacity: 1})

// gsap.fromTo('.question', {y: -100, opacity: 0}, {y: 0, delay: 1.25, duration: 1, opacity: 1})

// gsap.fromTo('label', {y: -100, opacity: 0}, {y: 0, delay: 1.5, duration: 1, opacity: 1})
// gsap.fromTo('input', {y: -100, opacity: 0}, {y: 0, delay: 1.5, duration: 1, opacity: 1})
// gsap.fromTo('textarea', {y: -100, opacity: 0}, {y: 0, delay: 1.5, duration: 1, opacity: 1})


