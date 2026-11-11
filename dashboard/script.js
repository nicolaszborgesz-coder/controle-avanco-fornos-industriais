
const API = "data.json";

const elemento = id => document.getElementById(id);

function formatar(valor) {
    return Number(valor).toFixed(2).replace(".", ",") + "%";
}

async function carregarDashboard() {

    const botao = elemento("refreshBtn");

    botao.disabled = true;

    try {

        const resposta = await fetch(
            `${API}?t=${Date.now()}`
        );

        if (!resposta.ok) {
            throw new Error("Não foi possível carregar os dados.");
        }

        const dados = await resposta.json();

        atualizarIndicadores(dados.resumo);

        atualizarTabela(dados.etapas);

        desenharCurva(dados.curva);

        elemento("updatedAt").textContent =
            "Última atualização: " + dados.atualizado_em;

    } catch (erro) {

        console.error(erro);

        elemento("updatedAt").textContent =
            "Erro ao atualizar os dados. Execute o Python.";

    } finally {

        botao.disabled = false;

    }
}


// ===================================
// INDICADORES
// ===================================

function atualizarIndicadores(resumo) {

    elemento("realizado").textContent =
        formatar(resumo.realizado);

    elemento("planejado").textContent =
        formatar(resumo.planejado);

    const desvio = Number(resumo.desvio);

    const campo = elemento("desvio");

    campo.textContent =
        `${desvio > 0 ? "+" : ""}${desvio.toFixed(2).replace(".", ",")} p.p.`;

    campo.style.color =
        desvio >= 0 ? "#22c55e" : "#f87171";

    elemento("totalEtapas").textContent =
        resumo.total_etapas;

    elemento("concluidas").textContent =
        `${resumo.concluidas} concluídas`;

}


// ===================================
// TABELA DE ETAPAS
// ===================================

function atualizarTabela(etapas) {

    const corpo = elemento("stageRows");

    corpo.replaceChildren();

    etapas.forEach(etapa => {

        const linha = document.createElement("tr");

        const valores = [
            etapa.etapa,
            `${etapa.peso}%`,
            formatar(etapa.planejado),
            formatar(etapa.realizado),
            `${etapa.realizado - etapa.planejado > 0 ? "+" : ""}${(etapa.realizado - etapa.planejado).toFixed(2).replace(".", ",")} p.p.`
        ];

        valores.forEach((valor, indice) => {

            const celula = document.createElement("td");

            celula.textContent = valor;

            if (indice === 4) {

                celula.className =
                    etapa.realizado >= etapa.planejado
                        ? "positive"
                        : "negative";

            }

            linha.appendChild(celula);

        });

        corpo.appendChild(linha);

    });

}


// ===================================
// GRÁFICO CURVA S
// ===================================

function desenharCurva(curva) {

    const canvas = elemento("grafico-curva");

    const ctx = canvas.getContext("2d");

    const largura = canvas.clientWidth;

    const altura = canvas.clientHeight;

    const escala = window.devicePixelRatio || 1;

    canvas.width = largura * escala;

    canvas.height = altura * escala;

    ctx.setTransform(escala, 0, 0, escala, 0, 0);

    ctx.clearRect(0, 0, largura, altura);

    const margem = {
        esquerda: 40,
        direita: 20,
        superior: 15,
        inferior: 35
    };

    const graficoW =
        largura - margem.esquerda - margem.direita;

    const graficoH =
        altura - margem.superior - margem.inferior;

    const quantidade = curva.semanas.length;

    if (!quantidade) return;

    const x = i =>
        margem.esquerda +
        (quantidade === 1 ? graficoW / 2 :
        i * graficoW / (quantidade - 1));

    const y = valor =>
        margem.superior +
        graficoH -
        (valor / 100) * graficoH;


    // Linhas de referência

    ctx.font = "10px Arial";
    ctx.textAlign = "right";

    for (let valor = 0; valor <= 100; valor += 25) {

        const posicao = y(valor);

        ctx.strokeStyle = "#334155";

        ctx.beginPath();

        ctx.moveTo(margem.esquerda, posicao);

        ctx.lineTo(
            largura - margem.direita,
            posicao
        );

        ctx.stroke();

        ctx.fillStyle = "#94a3b8";

        ctx.fillText(
            `${valor}%`,
            margem.esquerda - 8,
            posicao + 3
        );

    }


    // Séries de dados

    const series = [
        {
            dados: curva.planejado,
            cor: "#3b82f6"
        },
        {
            dados: curva.realizado,
            cor: "#22c55e"
        }
    ];


    series.forEach(serie => {

        ctx.beginPath();

        serie.dados.forEach((valor, i) => {

            const px = x(i);

            const py = y(valor);

            if (i === 0) {
                ctx.moveTo(px, py);
            } else {
                ctx.lineTo(px, py);
            }

        });

        ctx.strokeStyle = serie.cor;

        ctx.lineWidth = 3;

        ctx.lineJoin = "round";

        ctx.stroke();


        // Marcadores

        serie.dados.forEach((valor, i) => {

            ctx.beginPath();

            ctx.arc(
                x(i),
                y(valor),
                3.5,
                0,
                Math.PI * 2
            );

            ctx.fillStyle = serie.cor;

            ctx.fill();

        });

    });


    // Identificação das semanas

    ctx.textAlign = "center";

    ctx.fillStyle = "#94a3b8";

    curva.semanas.forEach((semana, i) => {

        ctx.fillText(
            semana,
            x(i),
            altura - 10
        );

    });

}


// ===================================
// EVENTOS
// ===================================

elemento("refreshBtn").addEventListener(
    "click",
    carregarDashboard
);

window.addEventListener(
    "resize",
    carregarDashboard
);

carregarDashboard();
