// CURSOR GLOW
const glow = document.getElementById("cursor-glow");

document.addEventListener("mousemove", (e) => {
    glow.style.left = e.clientX + "px";
    glow.style.top = e.clientY + "px";
});
console.log("animations.js loaded");
// ==========================
// CUSTOM CURSOR + TRAIL
// ==========================
const cursor = document.getElementById("cursor");
const trails = document.querySelectorAll(".cursor-trail");

let trailPositions = [];

const TRAIL_LENGTH = trails.length;

for (let i = 0; i < TRAIL_LENGTH; i++) {
    trailPositions.push({ x: 0, y: 0 });
}

let mouse = { x: 0, y: 0 };
let lastMoveTime = Date.now();

document.addEventListener("mousemove", (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;

    lastMoveTime = Date.now();

    // main cursor
    cursor.style.left = mouse.x + "px";
    cursor.style.top = mouse.y + "px";

    // trail positions
    trailPositions.unshift({ x: mouse.x, y: mouse.y });
    trailPositions.pop();
});

// TRAIL ANIMATION
function animateTrail() {
    const now = Date.now();
    const idle = now - lastMoveTime;

    trails.forEach((dot, index) => {
        let pos = trailPositions[index];

        if (pos) {
            dot.style.left = pos.x + "px";
            dot.style.top = pos.y + "px";

            // 🔥 fade out when idle
            if (idle > 100) {
                dot.style.opacity = Math.max(0, 1 - (idle - 100) / 300);
            } else {
                dot.style.opacity = 0.5 - index * 0.02;
            }
        }
    });

    requestAnimationFrame(animateTrail);
}
animateTrail();


// ==========================
// HOVER EFFECT
// ==========================
const hoverElements = document.querySelectorAll("a, button");

hoverElements.forEach(el => {
    el.addEventListener("mouseenter", () => {
        cursor.classList.add("hover");
    });

    el.addEventListener("mouseleave", () => {
        cursor.classList.remove("hover");
    });
});


// ==========================
// PARTICLES BACKGROUND
// ==========================
const canvas = document.getElementById("particles");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
const particleCount = 100;

// CREATE PARTICLES
for (let i = 0; i < particleCount; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 1.2 + 0.5,
        dx: (Math.random() - 0.5) * 0.5,
        dy: (Math.random() - 0.5) * 0.5
    });
}

// ANIMATION LOOP
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // PARTICLES
    particles.forEach(p => {
        p.x += p.dx;
        p.y += p.dy;

        // bounce
        if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;

        // mouse attraction
        let dx = mouse.x - p.x;
        let dy = mouse.y - p.y;
        let dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 120) {
            p.x += dx * 0.01;
            p.y += dy * 0.01;
        }

        // draw particle
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255,0.7)";
        ctx.fill();
    });

    // CONNECT LINES
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            let dx = particles[i].x - particles[j].x;
            let dy = particles[i].y - particles[j].y;
            let dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < 100) {
                let hue = (Date.now() / 10 + dist) % 360;
                ctx.strokeStyle = `hsla(${hue}, 100%, 70%, ${1 - dist / 100})`;
                ctx.lineWidth = 0.3;
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }
        }
    }

    requestAnimationFrame(animate);
}

animate();


// ==========================
// RESIZE FIX
// ==========================
window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});