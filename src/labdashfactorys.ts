import { DNDNotebookPanel } from './dNDNotebookPanel'
import { Notebook, StaticNotebook, INotebookModel } from '@jupyterlab/notebook'
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { ABCWidgetFactory } from '@jupyterlab/docregistry';
import { IEditorMimeTypeService } from '@jupyterlab/codeeditor';
import { RenderMimeRegistry } from '@jupyterlab/rendermime';
import { CodeCell, MarkdownCell, RawCell } from '@jupyterlab/cells'
// import { Toolbar } from '@jupyterlab/apputils';


class LabDashPanel implements IReadyWidget(){
    
}


export class LabDashPanel extends ABCWidgetFactory<LabDashPanel, INotebookModel>  {
    private mimeTypeService: IEditorMimeTypeService
    private rendermime: RenderMimeRegistry

    constructor(options: DNDNotebookFactory.IOptions) {
        super(options)
        this.rendermime = options.rendermime;
        this.mimeTypeService = options.mimeTypeService;
    }


    createNewWidget(context: DocumentRegistry.IContext<INotebookModel>) {
        console.log('New widget from factory', context);
        let panel = new LabDashPanel({})
        panel.context = context
        
    
        return panel
    }

}


export namespace DNDNotebookFactory {
    /**
     * The options used to construct a `NotebookWidgetFactory`.
     */
    export interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
        rendermime: RenderMimeRegistry;
        mimeTypeService: IEditorMimeTypeService;
    }
}