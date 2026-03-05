// script.js - Scripturi comune pentru infograficele meridianelor

const colorPalette = {
    darkBlue: '#0A2463',
    mediumBlue: '#3E92CC',
    crimson: '#D8315B',
    yellow: '#F4C150',
    green: '#06D6A0',
    
    // Culori pale pentru meridiane (fundal body și carduri index)
    lungPale: '#e6f7ff',       // Metal - Plămân (Pale sky blue)
    heartPale: '#ffebe6',      // Foc - Inimă (Pale red/pink)
    pericardPale: '#fff0f5',   // Foc - Pericard (Pale rose)
    spleenPancreasPale: '#fffbe6', // Pământ - Splină-Pancreas (Pale yellow/beige)
    liverPale: '#e6fff2',      // Lemn - Ficat (Pale green)
    kidneyPale: '#e6efff',     // Apă - Rinichi (Pale blue)
    largeIntestinePale: '#f0f8ff', // Metal - Intestin Gros (Pale grey-blue)
    smallIntestinePale: '#fffaf0', // Foc - Intestin Subțire (Pale orange)
    tripleHeaterPale: '#fff5ee', // Foc - Triplu Încălzitor (Pale peach)
    stomachPale: '#fffaf0',    // Pământ - Stomac (Pale beige)
    urinaryBladderPale: '#f0f0ff', // Apă - Vezică Urinară (Pale lavender)
    gallbladderPale: '#f0fff0', // Lemn - Vezică Biliară (Pale mint green)
    governingVesselPale: '#fffacd', // Yang - Vas Guvernator (Pale gold)
    conceptionVesselPale: '#f8f8ff'  // Yin - Vas de Concepție (Pale silver-blue)
};

const tooltipConfig = {
    plugins: {
        tooltip: {
            callbacks: {
                title: function(tooltipItems) {
                    const item = tooltipItems[0];
                    let label = item.chart.data.labels[item.dataIndex];
                    if (Array.isArray(label)) {
                        return label.join(' ');
                    } else {
                        return label;
                    }
                }
            }
        },
        legend: {
            position: 'top',
            labels: {
                font: {
                    family: 'Inter',
                    size: 14
                },
                color: '#212529'
            }
        }
    }
};

function wrapLabel(label, maxLength = 16) {
    if (label.length <= maxLength) return label;
    const words = label.split(' ');
    const lines = [];
    let currentLine = '';
    words.forEach(word => {
        if ((currentLine + ' ' + word).length > maxLength && currentLine.length > 0) {
            lines.push(currentLine.trim());
            currentLine = word;
        } else {
            currentLine += (currentLine === '' ? '' : ' ') + word;
        }
    });
    lines.push(currentLine.trim());
    return lines;
}

// Script pentru a seta culorile de fundal ale cardurilor dinamic în index.html
document.addEventListener('DOMContentLoaded', () => {
    const meridianCards = document.querySelectorAll('.meridian-card');
    const colors = {
        'Meridianul plămân': colorPalette.lungPale,
        'Meridianul inimă': colorPalette.heartPale,
        'Meridianul pericard': colorPalette.pericardPale,
        'Meridianul splină-pancreas': colorPalette.spleenPancreasPale,
        'Meridianul ficat': colorPalette.liverPale,
        'Meridianul rinichi': colorPalette.kidneyPale,
        'Meridianul intestin gros': colorPalette.largeIntestinePale,
        'Meridianul intestin subțire': colorPalette.smallIntestinePale,
        'Meridianul triplu încălzitor': colorPalette.tripleHeaterPale,
        'Meridianul stomac': colorPalette.stomachPale,
        'Meridianul vezică urinară': colorPalette.urinaryBladderPale,
        'Meridianul vezică biliară': colorPalette.gallbladderPale,
        'Meridianul vas guvernator': colorPalette.governingVesselPale,
        'Meridianul vas de concepție': colorPalette.conceptionVesselPale,
    };

    meridianCards.forEach(card => {
        const title = card.querySelector('h3').textContent.trim();
        if (colors[title]) {
            card.style.backgroundColor = colors[title];
        }
    });
});

// Script de securitate pentru a bloca copierea și uneltele de dezvoltator
document.addEventListener('contextmenu', event => event.preventDefault()); // Blochează clicul dreapta
document.addEventListener('keydown', function(e) {
        // Blochează Ctrl+C (Copiere)
        if (e.ctrlKey && e.key === 'c') {
            e.preventDefault();
        }
        // Blochează Ctrl+U (View Source)
        if (e.ctrlKey && e.key === 'u') {
            e.preventDefault();
        }
        // Blochează F12 (Developer Tools)
        if (e.key === 'F12') {
            e.preventDefault();
        }
        // Blochează Ctrl+Shift+I (Developer Tools)
        if (e.ctrlKey && e.shiftKey && e.key === 'I') {
            e.preventDefault();
        }
        // Blochează Ctrl+Shift+J (Developer Tools Console)
        if (e.ctrlKey && e.shiftKey && e.key === 'J') {
            e.preventDefault();
        }
});

