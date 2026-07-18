import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Home from './page';

describe('Home Page', () => {
    it('renders the hero section correctly', () => {
        render(<Home />);

        // Check for the main heading
        expect(screen.getByText(/Chat → Nota →/)).toBeInTheDocument();
        expect(screen.getByText('Selesai.')).toBeInTheDocument();

        // Check for the CTA button
        expect(screen.getByText('Mulai via WhatsApp')).toBeInTheDocument();

        // Check for features
        expect(screen.getByText('Nota PDF Otomatis')).toBeInTheDocument();
        expect(screen.getByText('Rekap Harian')).toBeInTheDocument();
        expect(screen.getByText('Voice Note')).toBeInTheDocument();
    });
});
