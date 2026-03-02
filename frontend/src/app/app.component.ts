import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Header } from './header/header';
import { Footer } from './footer/footer';
import { SidebarComponent } from './sidebar/sidebar';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [RouterOutlet, Header, Footer, SidebarComponent],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})
export class AppComponent {
    title = 'frontend';
    isSidebarCollapsed = false;

    toggleSidebar() {
        this.isSidebarCollapsed = !this.isSidebarCollapsed;
    }
}
