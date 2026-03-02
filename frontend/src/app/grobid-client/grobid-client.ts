import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-grobid-client',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './grobid-client.html',
  styleUrl: './grobid-client.css'
})
export class GrobidClientComponent {
  selectedFile: File | null = null;
  isLoading = false;
  result: string | null = null;
  jats: string | null = null;
  error: string | null = null;
  metadataForm: FormGroup;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private fb: FormBuilder) {
    this.metadataForm = this.fb.group({
      title: [''],
      journal: [''],
      publisher: [''],
      date: [''],
      doi: [''],
      abstract: [''],
      license_text: [''],
      license_url: [''],
      volume: [''],
      issue: [''],
      fpage: [''],
      lpage: [''],
      authors: this.fb.array([]),
      keywords: this.fb.array([]),
      issn: this.fb.array([])
    });
  }

  get authors() {
    return this.metadataForm.get('authors') as FormArray;
  }

  get keywords() {
    return this.metadataForm.get('keywords') as FormArray;
  }

  get issn() {
    return this.metadataForm.get('issn') as FormArray;
  }

  addAuthor(author: any = { first_name: '', last_name: '', affiliation: '' }) {
    this.authors.push(this.fb.group({
      first_name: [author.first_name || ''],
      last_name: [author.last_name || ''],
      affiliation: [author.affiliation || '']
    }));
  }

  removeAuthor(index: number) {
    this.authors.removeAt(index);
  }

  addKeyword(keyword: string = '') {
    this.keywords.push(this.fb.control(keyword));
  }

  removeKeyword(index: number) {
    this.keywords.removeAt(index);
  }

  addIssn(issn: string = '') {
    this.issn.push(this.fb.control(issn));
  }

  removeIssn(index: number) {
    this.issn.removeAt(index);
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.result = null;
    this.jats = null;
    this.error = null;
    this.metadataForm.reset();
    this.authors.clear();
    this.keywords.clear();
    this.issn.clear();
  }

  uploadFile() {
    if (!this.selectedFile) return;

    this.isLoading = true;
    this.result = null;
    this.jats = null;
    this.error = null;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http.post<any>('http://localhost:8000/grobid/', formData)
      .pipe(finalize(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }))
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            this.result = response.tei;
            this.jats = response.jats;

            // Populate form
            const metadata = response.metadata;
            this.metadataForm.patchValue({
              title: metadata.title,
              journal: metadata.journal,
              publisher: metadata.publisher,
              date: metadata.date,
              doi: metadata.doi,
              abstract: metadata.abstract,
              license_text: metadata.license_text,
              license_url: metadata.license_url
            });

            this.authors.clear();
            if (metadata.authors) {
              metadata.authors.forEach((author: any) => this.addAuthor(author));
            }

            this.keywords.clear();
            if (metadata.keywords) {
              metadata.keywords.forEach((keyword: string) => this.addKeyword(keyword));
            }

            this.issn.clear();
            if (metadata.issn) {
              metadata.issn.forEach((issn: string) => this.addIssn(issn));
            }

          } else {
            this.error = response.message || 'Unknown error occurred';
          }
        },
        error: (err) => {
          this.error = err.error?.message || 'Failed to communicate with server';
        }
      });
  }

  generateJats() {
    if (!this.result) return;

    this.isLoading = true;
    this.error = null;

    const payload = {
      tei: this.result,
      metadata: this.metadataForm.value
    };

    this.http.post<any>('http://localhost:8000/grobid/api/generate-jats', payload)
      .pipe(finalize(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }))
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            this.jats = response.jats;
          } else {
            this.error = response.message || 'Unknown error occurred';
          }
        },
        error: (err) => {
          this.error = err.error?.message || 'Failed to communicate with server';
        }
      });
  }
}
