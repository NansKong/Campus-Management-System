import api from './api';
import attendanceService from './attendanceService';
import foodService from './foodService';
import remedialService from './remedialService';
import studentService from './studentService';

jest.mock('./api', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
}));

describe('service smoke contracts', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('attendance sections endpoint contract', async () => {
    api.get.mockResolvedValue({ data: [] });
    await attendanceService.getMySections();
    expect(api.get).toHaveBeenCalledWith('/attendance/sections/my');
  });

  test('food order status update contract', async () => {
    api.put.mockResolvedValue({ data: { message: 'ok' } });
    await foodService.updateOrderStatus('order-1', 'ready');
    expect(api.put).toHaveBeenCalledWith('/food/orders/order-1/status', { status: 'ready' });
  });

  test('remedial attendance mark contract', async () => {
    api.post.mockResolvedValue({ data: { success: true } });
    await remedialService.markAttendance('ABC123');
    expect(api.post).toHaveBeenCalledWith('/remedial/attendance/mark', {
      remedial_code: 'ABC123',
    });
  });

  test('student list query contract', async () => {
    api.get.mockResolvedValue({ data: [] });
    await studentService.listStudents({ search: 'riya' });
    expect(api.get).toHaveBeenCalledWith('/students', { params: { search: 'riya' } });
  });
});
