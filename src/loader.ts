export class Progress{
    private ele:HTMLDivElement;
    private _progress:number = 0;
    private _target:number = 100;
    private _started:boolean = false;
    public hideOnDone = true;

    start(){
        if(!this._started){
            this.restart()
        }
    }
    restart(){
        if(this.ele){
            this._progress = 0;
            this.ele.parentElement.removeChild(this.ele);
        }
        this.ele = document.createElement('div');
        this.ele.classList.add('loader');
        this.ele.innerText = 'Loading...'
        document.body.appendChild(this.ele);
        this._started = true;
    }
    
    private updateProgress(val:number){
        this._progress = val;
        this.ele.innerText = `${this._progress}/${this._target} done`
        if(this._progress >= this._target && this.hideOnDone) {
            this.ele.style.display = 'none'
        }
    }

    set progress(val:number){
        this.updateProgress(val)
    }
    incProgress(val:number){
        this.updateProgress( this._progress +=val);
    }

    set target(val:number){
        this._target = val;
        this.updateProgress(this._progress);
    }
}

let _theProgress = new Progress();

export function getProgressInstance(){
    return _theProgress;
}