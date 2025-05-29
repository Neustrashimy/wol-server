document.addEventListener('DOMContentLoaded', () => {

    const I18N = window.I18N || {};

    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const action = btn.dataset.action;
            const id = btn.dataset.id;
            const row = document.getElementById(`row-${id}`);
            const statusCell = document.getElementById(`status-${id}`);

            let endpoint = `/api/${action}/${id}`;
            let init = { method: 'POST' };

            if (action === 'delete' && !confirm(I18N.deleteConfirm)) {
                return;
            }

            try {
                const res = await fetch(endpoint, init);
                const json = await res.json();
                if (!json.success) {
                    alert(`${I18N.errorPrefix}${json.error || res.statusText}`);
                    return;
                }

                // 成功時の画面更新
                switch (action) {
                    case 'wake':
                        //alert(I18N.wakeSuccess);
                        break;
                    case 'delete':
                        row.remove();
                        break;
                    case 'ping':
                        statusCell.textContent = json.status;
                        break;
                }
            } catch (err) {
                console.error(err);
                alert(I18N.fetchError);
            }
        });
    });
});
