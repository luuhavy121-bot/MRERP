// Synthetic fixtures only. Shared identity is declared, never inferred from customer data.
export type DemoOrder = {id:string;date:string;name:string;phone:string;address:string;product:string;price:number;quantity:number;value:number;delivery:string;processing:string;payment:string;origin:string;sources:string[]}
export const demoSources=['Webcake','POS','Google Sheet']
export const demoDeliveryStates=['Chưa bàn giao','Đang giao','Giao thành công','Hoàn hàng','Đã hủy']
const names=['Nguyễn Minh Anh','Trần Quốc Bảo','Lê Thu Hà','Phạm Đức Long','Vũ Ngọc Mai','Đỗ Tuấn Kiệt','Hoàng Thanh Tâm','Bùi Gia Linh','Đặng Hải Nam','Phan Ngọc Hân']
const products=[{name:'Bình giữ nhiệt 500 ml',price:249000},{name:'Đèn bàn học',price:389000},{name:'Bộ hộp thực phẩm',price:179000},{name:'Gối tựa lưng',price:299000},{name:'Kệ để bàn',price:459000}]
const states=['Giao thành công','Giao thành công','Đang giao','Chưa bàn giao','Hoàn hàng','Đã hủy']
export const demoOrders:DemoOrder[]=Array.from({length:60},(_,i)=>{
 const p=products[i%5],quantity=1+i%3,delivery=states[i%6],origin=demoSources[i%3]
 return {id:`DEMO-${String(i+1).padStart(4,'0')}`,date:`2026-10-${String(1+Math.floor(i/2)).padStart(2,'0')}`,name:names[i%10],phone:`SĐT giả ${String(i+1).padStart(4,'0')}`,address:`Địa chỉ minh họa ${i+1}, không dùng giao hàng`,product:p.name,price:p.price,quantity,value:p.price*quantity,delivery,processing:delivery==='Chưa bàn giao'?'Chờ xác nhận':delivery==='Đã hủy'?'Đã hủy':'Đã xác nhận',payment:delivery==='Giao thành công'?'Chờ đối soát COD':['Hoàn hàng','Đã hủy'].includes(delivery)?'Không thu':'Chưa thu',origin,sources:i%5===0?[origin,demoSources[(i%3+1)%3]]:[origin]}
})
export const money=(n:number)=>new Intl.NumberFormat('vi-VN',{style:'currency',currency:'VND',maximumFractionDigits:0}).format(n)
export const date=(s:string)=>s.split('-').reverse().join('/')
