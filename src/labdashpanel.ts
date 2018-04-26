import { Panel } from '@phosphor/widgets';
import { NotebookJSON } from './notebook';
import { RenderMimeRegistry, standardRendererFactories, MimeModel } from '@jupyterlab/rendermime';
import { SimplifiedOutputArea, OutputAreaModel } from '@jupyterlab/outputarea'
import { Kernel, KernelMessage } from '@jupyterlab/services';
import { DocumentRegistry } from '@jupyterlab/docregistry'
import { editorServices } from '@jupyterlab/codemirror';
import bokeh_plugin from 'jupyterlab_bokeh/lib'
import widgetManagerProvider from '@jupyter-widgets/jupyterlab-manager'
import { /* Notebook, */ NotebookWidgetFactory, /* NotebookModelFactory, */ NotebookPanel } from '@jupyterlab/notebook';
import { each } from '@phosphor/algorithm';


class CodeCellWidget extends SimplifiedOutputArea {
    public number: number;
    private kernel: Kernel.IKernel;

    constructor(cell_number: number, k: Kernel.IKernel, rendermime: RenderMimeRegistry) {
        let outputModel = new OutputAreaModel({trusted:true})
        super({ rendermime, model: outputModel })
        this.number = cell_number
        this.kernel = k;
    }

    public run() {
        let msg = KernelMessage.createShellMessage({
            session: this.kernel.clientId, msgType: 'run_cell', channel: 'shell'
        },
            { 'cell_number': this.number }
        )
        this.future = this.kernel.sendShellMessage(msg, true)
    }
}





export class LabDashPanel extends Panel {
    private nb: NotebookJSON;
    private rendermime: RenderMimeRegistry = new RenderMimeRegistry({ initialFactories: standardRendererFactories });
    private kernel: Kernel.IKernel;

    constructor(k: Kernel.IKernel, nb: NotebookJSON) {
        super();
        this.nb = nb;
        this.kernel = k
        this._augmentRendermime()
        this._build()
    }

    private _augmentRendermime() {
        // hijack the jupyterlab plug in system by 'acting' a little like a JupyterLab application. This is to update the rendermime
        let docRegistry = new DocumentRegistry();
        //let mFactory = new NotebookModelFactory({});
        let editorFactory = editorServices.factoryService.newInlineEditor;
        let contentFactory = new NotebookPanel.ContentFactory({ editorFactory });
        let wFactory = new NotebookWidgetFactory({
            name: 'Notebook',
            modelName: 'notebook',
            fileTypes: ['notebook'],
            defaultFor: ['notebook'],
            preferKernel: true,
            canStartKernel: true,
            rendermime: this.rendermime,
            contentFactory,
            mimeTypeService: editorServices.mimeTypeService
        });
        docRegistry.addWidgetFactory(wFactory)
        let mocApp = { docRegistry: docRegistry };
        widgetManagerProvider.activate(mocApp as any)
        bokeh_plugin.activate(mocApp as any)
        let context = {
            session: {
                kernel:this.kernel,
                kernelChanged: {
                    connect: () => { }
                }
            }
        }
        let panel = { rendermime: this.rendermime }
        
        each(docRegistry.widgetExtensions('Notebook'), (ext) => {
            ext.createNew(panel as any, context as any)
        })
        // new NBWidgetExtension({ rendermime: this.rendermime }, {
        //     session: {
        //         kernel:this.kernel,
        //         kernelChanged: {
        //             connect: () => { }
        //         }
        //     }
        // })
    }

    private _build(): void {
        let cell_count = 0;
        for (let cell of this.nb.cells) {
            if (cell.cell_type == 'code') {
                let outputWidget = new CodeCellWidget(cell_count, this.kernel, this.rendermime)
                this.addWidget(outputWidget)
                outputWidget.run()
            } else if (cell.cell_type == 'markdown') {
                let mimeModel = new MimeModel({ data: { 'text/markdown': cell.source } });
                let render = this.rendermime.createRenderer('text/markdown');
                this.addWidget(render);
                render.renderModel(mimeModel);
            } else {
                console.warn('Can not render cell type ', cell.cell_type, cell)
            }
            cell_count++
        }
    }
}