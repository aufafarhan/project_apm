document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS
    AOS.init({ duration: 800, once: true });

    const form = document.getElementById('predict-form');
    const emptyState = document.getElementById('empty-state');
    const populatedState = document.getElementById('populated-state');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    const btnPredict = document.getElementById('btn-predict');
    const rekomendasiCard = document.getElementById('rekomendasi-card');
    const btnHistory = document.getElementById('btn-clear-history');

    let comparisonChart = null;

    // Load History
    loadHistory();

    if (btnHistory) {
        btnHistory.addEventListener('click', () => {
            localStorage.removeItem('jabarPredictHistory');
            loadHistory();
        });
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide error, set loading state
        errorAlert.style.display = 'none';
        const originalBtnText = btnPredict.innerHTML;
        btnPredict.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Memproses...';
        btnPredict.disabled = true;

        const data = {
            wilayah: document.getElementById('wilayah').value,
            tahun: parseInt(document.getElementById('tahun').value),
            ipm: parseFloat(document.getElementById('ipm').value),
            rls: parseFloat(document.getElementById('rls').value),
            tpt: parseFloat(document.getElementById('tpt').value),
            pdrb: parseFloat(document.getElementById('pdrb').value)
        };

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Terjadi kesalahan pada server');
            }

            const result = await response.json();
            
            // Render UI
            renderDashboard(result);
            saveHistory(result);
            loadHistory();

            // Smooth scroll to dashboard
            document.getElementById('dashboard-section').scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            errorMessage.textContent = error.message;
            errorAlert.style.display = 'flex';
        } finally {
            btnPredict.innerHTML = originalBtnText;
            btnPredict.disabled = false;
        }
    });

    function renderDashboard(data) {
        emptyState.style.display = 'none';
        populatedState.style.display = 'block';

        // Summary Cards
        document.getElementById('sum-wilayah').textContent = data.wilayah;
        document.getElementById('sum-tahun').textContent = data.tahun;
        document.getElementById('sum-angka').textContent = data.prediksi_penduduk_miskin.toLocaleString('id-ID');
        
        const badge = document.getElementById('sum-badge');
        badge.textContent = data.klasifikasi;
        badge.className = 'badge badge-lg font-bold px-4 py-3 border-none text-white';
        if (data.klasifikasi === 'Rendah') badge.classList.add('bg-success');
        else if (data.klasifikasi === 'Sedang') badge.classList.add('bg-warning');
        else if (data.klasifikasi === 'Tinggi') badge.classList.add('bg-error');
        else badge.classList.add('bg-primary');

        // Interpretasi
        document.getElementById('res-penjelasan').innerHTML = data.penjelasan_model.replace(/\n/g, '<br>');

        // Chart
        renderChart(data);

        // Status Indikator
        updateStatus('ipm', data.input_data.ipm, data.regional_average.ipm, true);
        updateStatus('rls', data.input_data.rls, data.regional_average.rls, true);
        updateStatus('tpt', data.input_data.tpt, data.regional_average.tpt, false);
        updateStatus('pdrb', data.input_data.pdrb, data.regional_average.pdrb, true);

        // Rekomendasi
        generateRekomendasi(data.input_data, data.regional_average);
    }

    function updateStatus(key, val, avg, higherIsBetter) {
        document.getElementById(`stat-${key}-val`).textContent = val.toFixed(2);
        document.getElementById(`stat-${key}-avg`).textContent = avg.toFixed(2);
        
        const badge = document.getElementById(`stat-${key}-badge`);
        let status = '';
        let color = '';
        
        const diff = (val - avg) / avg * 100;
        
        if (higherIsBetter) {
            if (diff >= 5) { status = 'Lebih Baik'; color = 'bg-success/20 text-success border-success/30'; }
            else if (diff <= -5) { status = 'Perlu Perhatian'; color = 'bg-error/20 text-error border-error/30'; }
            else { status = 'Mendekati Rata-rata'; color = 'bg-warning/20 text-warning border-warning/30'; }
        } else {
            if (diff <= -5) { status = 'Lebih Baik'; color = 'bg-success/20 text-success border-success/30'; }
            else if (diff >= 5) { status = 'Perlu Perhatian'; color = 'bg-error/20 text-error border-error/30'; }
            else { status = 'Mendekati Rata-rata'; color = 'bg-warning/20 text-warning border-warning/30'; }
        }

        badge.textContent = status;
        badge.className = `badge badge-sm py-2.5 px-3 font-bold w-full text-[10px] ${color}`;
    }

    function generateRekomendasi(input, avg) {
        const gaps = [
            { key: 'IPM', val: (avg.ipm - input.ipm) / avg.ipm, msg: 'Peningkatan akses kesehatan dan kualitas pendidikan dasar.' },
            { key: 'RLS', val: (avg.rls - input.rls) / avg.rls, msg: 'Program pencegahan putus sekolah dan beasiswa pendidikan.' },
            { key: 'TPT', val: (input.tpt - avg.tpt) / avg.tpt, msg: 'Penciptaan lapangan kerja padat karya dan pelatihan vokasi.' },
            { key: 'PDRB', val: (avg.pdrb - input.pdrb) / Math.abs(avg.pdrb), msg: 'Stimulus ekonomi untuk UMKM dan investasi daerah.' }
        ];

        gaps.sort((a, b) => b.val - a.val);
        const worst = gaps[0];

        rekomendasiCard.classList.remove('hidden');
        if (worst.val > 0.05) {
            document.getElementById('rekomendasi-title').textContent = `Prioritas Intervensi: ${worst.key}`;
            document.getElementById('rekomendasi-text').textContent = `Indikator ${worst.key} di wilayah ini terpaut cukup jauh dari rata-rata Jawa Barat. Rekomendasi kebijakan: ${worst.msg}`;
            rekomendasiCard.querySelector('i').className = 'fas fa-exclamation-circle text-2xl text-error animate-pulse mt-1';
            rekomendasiCard.className = 'alert bg-[#1a0040]/80 border border-error/30 shadow-[0_0_15px_rgba(239,68,68,0.2)] transition-all-smooth';
        } else {
            document.getElementById('rekomendasi-title').textContent = 'Kondisi Relatif Stabil';
            document.getElementById('rekomendasi-text').textContent = 'Seluruh indikator makro berada pada atau lebih baik dari rata-rata Jawa Barat. Pertahankan tren positif ini.';
            rekomendasiCard.querySelector('i').className = 'fas fa-check-circle text-2xl text-success mt-1';
            rekomendasiCard.className = 'alert bg-[#1a0040]/80 border border-success/30 shadow-[0_0_15px_rgba(34,197,94,0.2)] transition-all-smooth';
        }
    }

    function renderChart(data) {
        const canvas = document.getElementById('comparisonChart');
        
        // Destroy existing chart using Chart.js built-in getChart method
        let existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        comparisonChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['IPM', 'RLS', 'TPT', 'PDRB'],
                datasets: [
                    {
                        label: 'Input Wilayah',
                        data: [data.input_data.ipm, data.input_data.rls, data.input_data.tpt, data.input_data.pdrb],
                        backgroundColor: '#00d2ff',
                        borderRadius: 4
                    },
                    {
                        label: 'Rata-rata Jabar',
                        data: [data.regional_average.ipm, data.regional_average.rls, data.regional_average.tpt, data.regional_average.pdrb],
                        backgroundColor: 'rgba(255, 255, 255, 0.2)',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: 'rgba(255,255,255,0.7)' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: 'rgba(255,255,255,0.7)' }
                    }
                }
            }
        });
    }

    function saveHistory(data) {
        let history = JSON.parse(localStorage.getItem('jabarPredictHistory') || '[]');
        const entry = {
            waktu: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
            wilayah: data.wilayah,
            tahun: data.tahun,
            prediksi: data.prediksi_penduduk_miskin,
            kategori: data.klasifikasi
        };
        history.unshift(entry);
        if (history.length > 5) history.pop();
        localStorage.setItem('jabarPredictHistory', JSON.stringify(history));
    }

    function loadHistory() {
        const historyTable = document.getElementById('history-tbody');
        if (!historyTable) return;
        
        let history = JSON.parse(localStorage.getItem('jabarPredictHistory') || '[]');
        if (history.length === 0) {
            historyTable.innerHTML = '<tr><td colspan="5" class="text-center text-white/40 py-6">Belum ada riwayat prediksi</td></tr>';
            return;
        }

        historyTable.innerHTML = history.map((h, i) => `
            <tr class="hover:bg-white/5 border-b border-white/5 transition-colors">
                <td class="font-mono text-xs text-white/50">${h.waktu}</td>
                <td class="font-semibold text-white">${h.wilayah}</td>
                <td class="text-white/70">${h.tahun}</td>
                <td class="font-bold text-[#ff6fd8]">${h.prediksi.toLocaleString('id-ID')}</td>
                <td>
                    <span class="badge badge-sm border-none ${
                        h.kategori === 'Rendah' ? 'bg-success text-success-content' : 
                        h.kategori === 'Sedang' ? 'bg-warning text-warning-content' : 
                        h.kategori === 'Tinggi' ? 'bg-error text-error-content' : 'bg-primary'
                    }">${h.kategori}</span>
                </td>
            </tr>
        `).join('');
    }
});
