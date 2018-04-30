
import '@jupyterlab/theme-light-extension/static/index.css';
import '@jupyterlab/application/style/index.css';
import '../assets/index.css'
import {getProgressInstance} from './loader';
getProgressInstance().start();

import { KernelManager, Kernel } from '@jupyterlab/services';
import { Widget } from '@phosphor/widgets';
import { LabDashPanel } from './labdashpanel';
import { NotebookJSON } from './notebook';



function attachToBody(widget: Widget) {
    // Attach the panel to the DOM.
    Widget.attach(widget, document.body);

    // Handle resize events.
    window.addEventListener('resize', () => { widget.update(); });
}

function build_kernel_name(notebook: NotebookJSON) {
    return JSON.stringify({ notebook: notebook.path })
}
function start(kManager: KernelManager): void {
    let match = location.search.match(/notebook=([^&]*)/)
    let notebook = (match)? unescape(match[1]) : 'simple.widgets.ipynb';
    fetch('/api/notebooks/' + notebook).then(res => res.text()).then(JSON.parse).then(nb => {
        nb.path = notebook;
        loadnb(kManager, nb as NotebookJSON)
    })
}


function loadnb(km: Kernel.IManager, nb: NotebookJSON) {
    console.log(nb);
    km.startNew({ 'name': build_kernel_name(nb) }).then(k => runNotebook(k, nb))
}


function runNotebook(k: Kernel.IKernel, nb: NotebookJSON) {
    let panel = new LabDashPanel(k, nb);
    attachToBody(panel)
}

export function main(): void {
    let manager = new KernelManager();
    manager.ready.then(() => {
        start(manager)
    });
}


window.addEventListener('load', main);
