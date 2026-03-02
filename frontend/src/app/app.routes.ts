import { Routes } from '@angular/router';
import { GrobidClientComponent } from './grobid-client/grobid-client';
import { Home } from './home/home';

export const routes: Routes = [
    { path: '', component: Home },
    { path: 'grobid', component: GrobidClientComponent }
];
