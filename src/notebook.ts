export interface NotebookJSON {
    cells: Array<Cell>
    path:string
}

export interface Cell {
    cell_type:CellType
        source:string
}
export enum CellType {
    code = "code",
    markdown = "markdown"
}