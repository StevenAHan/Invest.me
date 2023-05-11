function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
      currentDate = Date.now();
    } while (currentDate - date < milliseconds);
  }

gsap.fromTo('.prompt-container', {y: 100, opacity: 0}, {y: 0, duration: 1, opacity: 1})
gsap.fromTo('.prompt-bigtitle', {y: -100, opacity: 0}, {y: 0, duration: .5, opacity: 1})
gsap.fromTo('.question', {x: -100, opacity: 0}, {x: 0, duration: 1, opacity: 1})


