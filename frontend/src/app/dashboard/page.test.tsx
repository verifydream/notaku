import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DashboardPage from './page';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('Dashboard Page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Mock window.location
        Object.defineProperty(window, 'location', {
            value: { search: '' },
            writable: true
        });
    });

    it('renders phone input when no phone parameter', () => {
        render(<DashboardPage />);
        expect(screen.getByText('📒 NotaKu Dashboard')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('081234567890')).toBeInTheDocument();
    });

    it('fetches and displays dashboard data when phone is provided in form', async () => {
        mockFetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                date: "2026-07-17",
                total_sales: 150000,
                total_expenses: 50000,
                profit: 100000,
                transaction_count: 2
            })
        }).mockResolvedValueOnce({
            ok: true,
            json: async () => ([
                {
                    id: "tx1",
                    total: 150000,
                    type: "sale",
                    note: null,
                    created_at: "2026-07-17T12:00:00Z",
                    items: [{ id: "item1", menu_item_name: "Nasi Uduk", quantity: 3, unit_price: 50000, subtotal: 150000 }]
                }
            ])
        });

        render(<DashboardPage />);

        // Enter phone
        const input = screen.getByPlaceholderText('081234567890');
        fireEvent.change(input, { target: { value: '08111222' } });

        // Submit
        fireEvent.click(screen.getByText('Lihat'));

        // Wait for dashboard to render
        await waitFor(() => {
            expect(screen.getByText('Dashboard untuk 08111222')).toBeInTheDocument();
        });

        // Check summary stats
        expect(screen.getByText('Rp 150.000')).toBeInTheDocument(); // Omset
        expect(screen.getByText('Rp 100.000')).toBeInTheDocument(); // Profit
        expect(screen.getByText('Rp 50.000')).toBeInTheDocument(); // Pengeluaran

        // Check transactions
        expect(screen.getByText('3x Nasi Uduk')).toBeInTheDocument();
    });
});
